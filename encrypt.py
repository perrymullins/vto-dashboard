#!/usr/bin/env python3
"""Encrypt data.json into the committed data.enc.json.

    python3 build/encrypt.py                 # prompt for passphrase
    python3 build/encrypt.py --generate      # invent a strong one and print it
    VTO_PASSPHRASE=... python3 build/encrypt.py

PBKDF2-SHA256 (600k iterations) -> AES-256-GCM, matching what the browser's
Web Crypto does on the other side. Only data.enc.json is ever committed; the
plaintext data.json stays gitignored.
"""

import base64
import getpass
import gzip
import hashlib
import json
import os
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ITERATIONS = 600_000

# Short, unambiguous words — no lookalike pairs, easy to read aloud on a call.
WORDS = """
abbey advent anchor anthem beacon bishop bridge candle canon chapel chalice
choir cloister compass covenant cypress deacon diocese dogwood ember gather
gospel granite harbor harvest hymnal juniper kindle lantern lectern liturgy
magnolia mission mosaic nectar orchard parish pasture pelican pilgrim prairie
psalter quarry rector refuge ripple sanctuary sequoia shepherd steeple summit
sycamore tabernacle thicket threshold trellis vestry vigil vineyard willow
""".split()


def derive(passphrase, salt):
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"),
                               salt, ITERATIONS, dklen=32)


def aes_gcm_encrypt(key, iv, plaintext):
    """AES-256-GCM. Uses the stdlib if available, else a vendored fallback."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).encrypt(iv, plaintext, None)
    except ImportError:
        pass
    import aesgcm  # local pure-python implementation
    return aesgcm.encrypt(key, iv, plaintext)


def generate_passphrase(n=5):
    return "-".join(secrets.choice(WORDS) for _ in range(n))


def main():
    src = os.path.join(ROOT, "data.json")
    if not os.path.exists(src):
        sys.exit("data.json not found — run build/extract.py first.")

    if "--generate" in sys.argv:
        passphrase = generate_passphrase()
        generated = True
    else:
        generated = False
        passphrase = os.environ.get("VTO_PASSPHRASE") or ""
        if not passphrase:
            passphrase = getpass.getpass("Passphrase: ")
            if passphrase != getpass.getpass("Confirm:    "):
                sys.exit("Passphrases did not match.")
        if len(passphrase) < 12:
            sys.exit("Use at least 12 characters.")

    with open(src, "rb") as f:
        raw = f.read()

    # gzip first: the payload is repetitive JSON and compresses ~8x, which
    # keeps the committed file small and the first paint fast.
    packed = gzip.compress(raw, 9)

    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    key = derive(passphrase, salt)
    ct = aes_gcm_encrypt(key, iv, packed)

    payload = {
        "v": 1,
        "kdf": {"name": "PBKDF2", "hash": "SHA-256", "iterations": ITERATIONS},
        "cipher": "AES-GCM",
        "encoding": "gzip",
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
    }

    out = os.path.join(ROOT, "data.enc.json")
    with open(out, "w") as f:
        json.dump(payload, f)

    print(f"plaintext   {len(raw)/1024:8.0f} KB")
    print(f"gzipped     {len(packed)/1024:8.0f} KB")
    print(f"encrypted   {os.path.getsize(out)/1024:8.0f} KB  -> {out}")

    if generated:
        print("\n" + "=" * 58)
        print("  PASSPHRASE — save this now, it is not stored anywhere")
        print("=" * 58)
        print(f"\n     {passphrase}\n")
        print("=" * 58)
        print("Anyone with this can read the dashboard. Anyone without it")
        print("cannot, even with full access to the repository.")
        print("To change it later: re-run this script and redeploy.")


if __name__ == "__main__":
    main()
