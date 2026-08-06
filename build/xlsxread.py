"""Minimal read-only .xlsx reader (stdlib only, no openpyxl/pandas).

Returns cells keyed by real Excel row number so build/config.py anchors can be
checked against the spreadsheet by eye.
"""

import re
import zipfile
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _col_index(ref):
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


class Sheet:
    def __init__(self, name, rows):
        self.name = name
        self.rows = rows  # {excel_row_number: {col_index: str}}

    def cell(self, row, col):
        return self.rows.get(row, {}).get(col, "")

    def row(self, row, width=None):
        r = self.rows.get(row, {})
        w = width if width is not None else (max(r) + 1 if r else 0)
        return [r.get(i, "") for i in range(w)]

    def row_numbers(self):
        return sorted(self.rows)

    def find_row(self, text, col=0, start=1):
        """First row at/after `start` whose `col` cell starts with `text`."""
        t = text.strip().lower()
        for n in self.row_numbers():
            if n >= start and self.cell(n, col).strip().lower().startswith(t):
                return n
        return None


class Workbook:
    def __init__(self, path):
        z = zipfile.ZipFile(path)
        shared = []
        try:
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss.iter(NS + "si"):
                shared.append("".join(t.text or "" for t in si.iter(NS + "t")))
        except KeyError:
            pass

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rmap = {r.get("Id"): r.get("Target") for r in rels}

        self.sheets = {}
        self.order = []
        for s in wb.iter(NS + "sheet"):
            name = s.get("name")
            target = rmap[s.get(RNS + "id")].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            self.sheets[name] = Sheet(name, self._read(z, target, shared))
            self.order.append(name)

    @staticmethod
    def _read(z, target, shared):
        ws = ET.fromstring(z.read(target))
        out = {}
        for r in ws.iter(NS + "row"):
            rn = int(r.get("r"))
            cells = {}
            for c in r.iter(NS + "c"):
                t = c.get("t")
                if t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(NS + "t"))
                else:
                    v = c.find(NS + "v")
                    if v is None or v.text is None:
                        continue
                    val = shared[int(v.text)] if t == "s" else v.text
                val = val.strip()
                if val:
                    cells[_col_index(c.get("r"))] = val
            if cells:
                out[rn] = cells
        return out

    def __getitem__(self, name):
        return self.sheets[name]


# ---------------------------------------------------------------- cell parsing

_MISSING = {"", "na", "n/a", "none", "-", "—", "unknown", "tbd"}
_NOT_TRACKED = re.compile(
    r"not\s+(recorded|tracked)|no\s+longer\s+centrally\s+tracked|"
    r"rolled\s+into|included\s+above|no\s+one\s+has\s+this\s+number",
    re.I,
)
_LEADING_NUM = re.compile(r"^\$?\s*(-?[\d,]+(?:\.\d+)?)")


def clean_number(raw):
    """Parse one cell into a schema value.

    Returns a float/int, None (missing), or a dict for not-tracked / dirty text.
    See SCHEMA.md "Value states".
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if s.lower() in _MISSING:
        return None
    if _NOT_TRACKED.search(s):
        return {"state": "not_tracked", "raw": s}

    try:
        return _round(float(s))
    except ValueError:
        pass

    m = _LEADING_NUM.match(s)
    if m:
        n = _round(float(m.group(1).replace(",", "")))
        return {"value": n, "raw": s}
    return {"state": "not_tracked", "raw": s}


def _round(n):
    """Kill float artifacts (0.28999999999999998, 4.0000000000000001E-3)."""
    r = round(n, 10)
    return int(r) if r == int(r) and abs(r) < 1e15 else r
