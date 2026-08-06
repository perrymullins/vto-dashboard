"""Pure-Python AES-256-GCM. Stdlib only.

Exists so the build has zero pip dependencies — the browser side uses Web
Crypto, this side just has to produce a matching ciphertext. Verified against
the NIST GCM test vectors in selftest().

Not constant-time. Fine here: it runs once at build time on a local machine
against data the operator already has in plaintext.
"""

_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")

_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36,
         0x6C, 0xD8, 0xAB, 0x4D]


def _xtime(a):
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def _expand_key(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [_SBOX[b] for b in t]
            t[0] ^= _RCON[i // nk - 1]
        elif nk > 6 and i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return w, nr


def _encrypt_block(w, nr, block):
    s = [list(block[i::4]) for i in range(4)]  # column-major -> row-major

    def add_round_key(rnd):
        for c in range(4):
            for r in range(4):
                s[r][c] ^= w[rnd * 4 + c][r]

    add_round_key(0)
    for rnd in range(1, nr + 1):
        for r in range(4):
            for c in range(4):
                s[r][c] = _SBOX[s[r][c]]
        for r in range(1, 4):
            s[r] = s[r][r:] + s[r][:r]
        if rnd != nr:
            for c in range(4):
                a = [s[r][c] for r in range(4)]
                s[0][c] = _mul(a[0], 2) ^ _mul(a[1], 3) ^ a[2] ^ a[3]
                s[1][c] = a[0] ^ _mul(a[1], 2) ^ _mul(a[2], 3) ^ a[3]
                s[2][c] = a[0] ^ a[1] ^ _mul(a[2], 2) ^ _mul(a[3], 3)
                s[3][c] = _mul(a[0], 3) ^ a[1] ^ a[2] ^ _mul(a[3], 2)
        add_round_key(rnd)

    return bytes(s[r][c] for c in range(4) for r in range(4))


# ------------------------------------------------------------------ GF(2^128)

def _gmul(x, y):
    z, v = 0, y
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= v
        v = (v >> 1) ^ 0xE1000000000000000000000000000000 if v & 1 else v >> 1
    return z


def _ghash(h, data):
    y = 0
    for i in range(0, len(data), 16):
        y = _gmul(y ^ int.from_bytes(data[i:i + 16].ljust(16, b"\0"), "big"), h)
    return y


def _pad16(b):
    return b + b"\0" * (-len(b) % 16)


def _gctr(w, nr, icb, data):
    if not data:
        return b""
    out = bytearray()
    ctr = int.from_bytes(icb, "big")
    for i in range(0, len(data), 16):
        ks = _encrypt_block(w, nr, ctr.to_bytes(16, "big"))
        chunk = data[i:i + 16]
        out += bytes(a ^ b for a, b in zip(chunk, ks))
        ctr = (ctr & ~0xFFFFFFFF) | ((ctr + 1) & 0xFFFFFFFF)
    return bytes(out)


def _gcm(key, iv, data, aad, encrypting):
    w, nr = _expand_key(key)
    h = int.from_bytes(_encrypt_block(w, nr, b"\0" * 16), "big")

    if len(iv) == 12:
        j0 = iv + b"\0\0\0\1"
    else:
        s = _ghash(h, _pad16(iv) + b"\0" * 8 + (len(iv) * 8).to_bytes(8, "big"))
        j0 = s.to_bytes(16, "big")

    icb = (int.from_bytes(j0, "big") & ~0xFFFFFFFF) | \
          ((int.from_bytes(j0, "big") + 1) & 0xFFFFFFFF)
    icb = icb.to_bytes(16, "big")

    ct = _gctr(w, nr, icb, data)
    body = _pad16(aad) + _pad16(ct if encrypting else data) + \
        (len(aad) * 8).to_bytes(8, "big") + \
        (len(ct if encrypting else data) * 8).to_bytes(8, "big")
    s = _ghash(h, body)
    tag = _gctr(w, nr, j0, s.to_bytes(16, "big"))
    return ct, tag


def encrypt(key, iv, plaintext, aad=b""):
    """Returns ciphertext || 16-byte tag, the layout Web Crypto expects."""
    ct, tag = _gcm(key, iv, plaintext, aad, True)
    return ct + tag


def decrypt(key, iv, ciphertext, aad=b""):
    ct, want = ciphertext[:-16], ciphertext[-16:]
    pt, tag = _gcm(key, iv, ct, aad, False)
    if not _consttime_eq(tag, want):
        raise ValueError("authentication tag mismatch")
    return pt


def _consttime_eq(a, b):
    if len(a) != len(b):
        return False
    r = 0
    for x, y in zip(a, b):
        r |= x ^ y
    return r == 0


def selftest():
    """NIST SP 800-38D test vectors."""
    cases = [
        # (key, iv, plaintext, aad, expected ct+tag)
        ("00" * 32, "00" * 12, "", "",
         "530f8afbc74536b9a963b4f1c4cb738b"),
        ("00" * 32, "00" * 12, "00" * 16, "",
         "cea7403d4d606b6e074ec5d3baf39d18d0d1c8a799996bf0265b98b5d48ab919"),
        ("feffe9928665731c6d6a8f9467308308feffe9928665731c6d6a8f9467308308",
         "cafebabefacedbaddecaf888",
         "d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a72"
         "1c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b39",
         "feedfacedeadbeeffeedfacedeadbeefabaddad2",
         "522dc1f099567d07f47f37a32a84427d643a8cdcbfe5c0c97598a2bd2555d1aa"
         "8cb08e48590dbb3da7b08b1056828838c5f61e6393ba7a0abcc9f662"
         "76fc6ece0f4e1768cddf8853bb2d551b"),
    ]
    for key, iv, pt, aad, want in cases:
        got = encrypt(bytes.fromhex(key), bytes.fromhex(iv),
                      bytes.fromhex(pt), bytes.fromhex(aad)).hex()
        assert got == want, f"FAIL\n got {got}\nwant {want}"
        back = decrypt(bytes.fromhex(key), bytes.fromhex(iv),
                       bytes.fromhex(want), bytes.fromhex(aad)).hex()
        assert back == pt, f"roundtrip FAIL: {back} != {pt}"
    return len(cases)


if __name__ == "__main__":
    print(f"aesgcm: {selftest()} NIST vectors pass")
