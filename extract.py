#!/usr/bin/env python3
"""Build data.json from the VTO workbook.

    python3 build/extract.py

Holds no per-tab logic — everything sheet-specific lives in config.py.
Writes plaintext only; run encrypt.py afterwards to produce the committed file.
"""

import datetime
import json
import os
import re
import sys

import config as C
from xlsxread import Workbook, clean_number

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


# ------------------------------------------------------------------- periods

_YEAR = re.compile(r"(19|20)\d{2}")


def period_year(label):
    """Sortable integer year for any period label.

    "2020 Jun" -> 2020        "2024-2025" -> 2025
    "2019 Jul - 2020 Jun" -> 2020    "12 mos. ending 2022-06-30" -> 2022
    """
    years = [int(m.group()) for m in _YEAR.finditer(str(label))]
    return max(years) if years else None


def is_blank(v):
    return v is None or (isinstance(v, dict) and v.get("state") == "not_tracked")


# -------------------------------------------------------------- block readers

def read_timeseries(sh, b):
    series = [dict(s) for s in b["series"]]
    first, last = b["rows"]
    rows = []
    for rn in range(first, last + 1):
        label = sh.cell(rn, 0).strip()
        if not label:
            continue
        values, raws = {}, {}
        for s in series:
            v = clean_number(sh.cell(rn, s["col"]))
            if isinstance(v, dict) and "value" in v:
                raws[s["id"]] = v["raw"]
                v = v["value"]
            values[s["id"]] = v
        note = sh.cell(rn, b["noteCol"]).strip() if b.get("noteCol") else ""
        if all(is_blank(v) for v in values.values()) and not note:
            # A period listed with no data at all is still meaningful (e.g.
            # "2025" with blanks means not-yet-reported), so keep it.
            pass
        row = {"period": label, "year": period_year(label), "values": values}
        if raws:
            row["raw"] = raws
        if note:
            row["note"] = note
        rows.append(row)
    for s in series:
        s.pop("col", None)
    return series, rows


def read_stacked(sh, b):
    """One spreadsheet column holding two different definitions stacked."""
    series, by_period = [], {}
    for spec in b["series"]:
        s = {k: v for k, v in spec.items() if k not in ("rows", "col")}
        series.append(s)
        first, last = spec["rows"]
        for rn in range(first, last + 1):
            label = sh.cell(rn, 0).strip()
            if not label:
                continue
            v = clean_number(sh.cell(rn, spec["col"]))
            raw = None
            if isinstance(v, dict) and "value" in v:
                raw, v = v["raw"], v["value"]
            r = by_period.setdefault(
                label, {"period": label, "year": period_year(label), "values": {}})
            r["values"][spec["id"]] = v
            if raw:
                r.setdefault("raw", {})[spec["id"]] = raw

    for r in by_period.values():
        for s in series:
            r["values"].setdefault(s["id"], None)
    rows = sorted(by_period.values(), key=lambda r: r["year"] or 0, reverse=True)
    return series, rows


def read_categorical(sh, b):
    """Rows are categories. Never a trend."""
    if "series" in b:
        series = [{k: v for k, v in s.items() if k != "col"} for s in b["series"]]
        first, last = b["rows"]
        rows = []
        for rn in range(first, last + 1):
            name = sh.cell(rn, b.get("nameCol", 0)).strip()
            if not name:
                continue
            values = {}
            for s in b["series"]:
                v = clean_number(sh.cell(rn, s["col"]))
                if isinstance(v, dict) and "value" in v:
                    v = v["value"]
                values[s["id"]] = v
            row = {"category": name, "values": values}
            if b.get("extraCol"):
                extra = sh.cell(rn, b["extraCol"]["col"]).strip()
                if extra:
                    row["extra"] = extra
            rows.append(row)
        return series, rows

    # Header-row form: categories come from a header row, values from one row.
    c0, c1 = b["cols"]
    series = [{"id": "value", "label": b.get("valueLabel", "Value"),
               "unit": "count", "format": "integer", "higherIsBetter": True}]
    rows = []
    for c in range(c0, c1 + 1):
        name = sh.cell(b["headerRow"], c).strip()
        if not name:
            continue
        v = clean_number(sh.cell(b["valueRow"], c))
        if isinstance(v, dict) and "value" in v:
            v = v["value"]
        rows.append({"category": name, "values": {"value": v}})
    return series, rows


def read_matrix(sh, b):
    """Rows are entities, columns are periods."""
    if "entities" in b:  # campus ministries: one small block per entity
        periods, rows = [], []
        for ent in b["entities"]:
            label, _hdr, first, last = ent[:4]
            # A block with no year header (a campus added under "ANY NEW CAMPUS
            # MISSIONS?") carries its period in the config instead. Without this
            # the entity's own name would be read as the period label.
            forced = ent[4] if len(ent) > 4 else None
            values, notes = {}, []
            for rn in range(first, last + 1):
                p = forced or sh.cell(rn, 0).strip()
                if not p:
                    continue
                v = clean_number(sh.cell(rn, 1))
                if isinstance(v, dict) and "value" in v:
                    v = v["value"]
                values[p] = v
                if p not in periods:
                    periods.append(p)
                note = sh.cell(rn, 2).strip()
                if note:
                    notes.append(f"{p}: {note}")
            row = {"entity": label, "values": values}
            if notes:
                row["note"] = "; ".join(notes)
            rows.append(row)
        periods.sort(key=lambda p: period_year(p) or 0)
        for r in rows:
            for p in periods:
                r["values"].setdefault(p, None)
        return periods, rows

    # schools: one wide block
    c0, c1 = b["cols"]
    periods = [sh.cell(b["headerRow"], c).strip() for c in range(c0, c1 + 1)]
    first, last = b["rows"]
    rows = []
    for rn in range(first, last + 1):
        name = sh.cell(rn, b["nameCol"]).strip()
        if not name:
            continue
        values = {}
        for i, c in enumerate(range(c0, c1 + 1)):
            v = clean_number(sh.cell(rn, c))
            if isinstance(v, dict) and "value" in v:
                v = v["value"]
            values[periods[i]] = v
        row = {"entity": name, "values": values}
        note = sh.cell(rn, b["noteCol"]).strip() if b.get("noteCol") else ""
        if note:
            row["note"] = note
        rows.append(row)
    return periods, rows


def read_irregular(sh, b):
    """Disaster: overlapping periods, text mixed into numeric cells."""
    periods = [p for _c, p in b["periods"]]
    rows = []
    for rn, label, unit in b["metricRows"]:
        values = {}
        for c, p in b["periods"]:
            cell = sh.cell(rn, c).strip()
            if unit == "text":
                values[p] = {"state": "text", "raw": cell} if cell else None
                continue
            v = clean_number(cell)
            if isinstance(v, dict) and "value" in v:
                values[p] = {"value": v["value"], "raw": v["raw"]}
            else:
                values[p] = v
        rows.append({"metric": label, "unit": unit, "values": values})
    return periods, rows


# ------------------------------------------------------------- tracking start

def apply_tracking_start(sec, warnings):
    """Rewrite pre-tracking values as not_tracked.

    A 0 recorded before a metric was collected is not a measurement. Left as a
    plotted zero it manufactures dramatic growth in the first real year, which
    is exactly the error this dashboard exists to prevent.
    """
    start = sec.get("trackingStart")
    if not start or sec["kind"] != "timeseries":
        return
    cutoff = period_year(start)
    years = [r["year"] for r in sec["rows"] if r.get("year")]
    if years and not (min(years) <= cutoff <= max(years)):
        warnings.append(
            f"{sec['id']}: trackingStart={start} is outside the data range "
            f"{min(years)}–{max(years)} — likely a typo")
    for row in sec["rows"]:
        if (row.get("year") or 0) >= cutoff:
            continue
        for k, v in row["values"].items():
            if v is None:
                continue
            row["values"][k] = {"state": "not_tracked",
                                "raw": f"recorded as {v} before tracking began"}
    sec["trackingStartYear"] = cutoff


# ------------------------------------------------------------------- assembly

def build():
    wb = Workbook(os.path.join(ROOT, "source", C.SOURCE))
    sections, warnings = [], []

    for b in C.BLOCKS:
        sh = wb[b["sheet"]]
        sec = {
            "id": b["id"], "tab": b["sheet"], "theme": b["theme"],
            "title": b["title"], "subtitle": b.get("subtitle"),
            "kind": {"timeseries": "timeseries", "stacked": "timeseries",
                     "categorical": "categorical", "matrix": "matrix",
                     "irregular": "irregular"}[b["type"]],
            "periodType": b.get("periodType", "year"),
            "trackingStart": b.get("trackingStart"),
            "owner": b.get("owner"),
        }
        for opt in ("population", "dimension", "tier", "headline",
                    "entityLabel", "valueLabel"):
            if b.get(opt):
                sec[opt] = b[opt]

        t = b["type"]
        if t == "timeseries":
            sec["series"], sec["rows"] = read_timeseries(sh, b)
        elif t == "stacked":
            sec["series"], sec["rows"] = read_stacked(sh, b)
        elif t == "categorical":
            sec["series"], sec["rows"] = read_categorical(sh, b)
        elif t == "matrix":
            sec["periods"], sec["rows"] = read_matrix(sh, b)
        elif t == "irregular":
            sec["periods"], sec["rows"] = read_irregular(sh, b)

        sec["notes"] = b.get("notes", [])
        sec["caveats"] = b.get("caveats", [])
        apply_tracking_start(sec, warnings)

        if not sec["rows"]:
            warnings.append(f"{b['id']}: produced no rows")
        sections.append(sec)

    ids = [s["id"] for s in sections]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        sys.exit(f"FATAL: duplicate section ids: {sorted(dupes)}")

    themes = []
    for tid, label, blurb in C.THEMES:
        members = [s["id"] for s in sections if s["theme"] == tid]
        if not members:
            warnings.append(f"theme '{tid}' has no sections")
        themes.append({"id": tid, "label": label, "blurb": blurb,
                       "sections": members})

    orphan = [s["id"] for s in sections
              if s["theme"] not in {t["id"] for t in themes}]
    if orphan:
        sys.exit(f"FATAL: sections in unknown themes: {orphan}")

    data = {
        "meta": {
            "schemaVersion": 1,
            "generated": datetime.date.today().isoformat(),
            "source": C.SOURCE,
            "reportingYear": C.REPORTING_YEAR,
            "latestDataYear": C.LATEST_DATA_YEAR,
            "baselineYear": C.BASELINE_YEAR,
        },
        "themes": themes,
        "sections": sections,
    }

    out = os.path.join(ROOT, "data.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # ------------------------------------------------------------- report
    by_tab = {}
    for s in sections:
        by_tab.setdefault(s["tab"], []).append(s)
    print(f"Wrote {out}  ({os.path.getsize(out)/1024:.0f} KB)\n")
    print(f"{'TAB':<16}{'SECTIONS':>9}{'ROWS':>7}")
    print("-" * 32)
    for tab in wb.order:
        secs = by_tab.get(tab, [])
        print(f"{tab:<16}{len(secs):>9}{sum(len(s['rows']) for s in secs):>7}")
    print("-" * 32)
    print(f"{'TOTAL':<16}{len(sections):>9}"
          f"{sum(len(s['rows']) for s in sections):>7}")

    caveats = sum(len(s["caveats"]) for s in sections)
    notes = sum(len(s["notes"]) for s in sections)
    tracking = [s["id"] for s in sections if s["trackingStart"]]
    print(f"\ncaveats: {caveats}   notes: {notes}   "
          f"tracking-start flags: {len(tracking)}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(" -", w)
    return data


if __name__ == "__main__":
    build()
