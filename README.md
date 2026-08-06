# EDOT VTO Dashboard

An interactive dashboard over the CMV VTO data ingathering workbook, built for
the Bishop's annual goal setting. It reads thirteen spreadsheet tabs of
differently-shaped mini-tables and presents them as ~70 metrics grouped into ten
themes, with the caveats surfaced rather than buried.

Branded to match the [EDOT Congregational Data
Dashboard](https://perrymullins.github.io/lobster-dashboard/).

## The passphrase

The dashboard holds clergy and staff demographics by race and gender, plus
entity-level finances. So `data.enc.json` — the only data file in this repo — is
**AES-256-GCM encrypted**. The repository can be public; without the passphrase
the committed file is unreadable, not merely hidden.

The passphrase is not stored anywhere in this repo. Share it out of band and
keep it in a password manager.

## Refreshing the data

Three commands. No `pip install` — everything uses the Python standard library.

```bash
# 1. Drop the new workbook in source/ and point config.py at it
#    (build/config.py, the SOURCE constant at the top)

# 2. Parse the workbook into plaintext data.json
python3 build/extract.py

# 3. Encrypt it into the file that actually gets committed
python3 build/encrypt.py          # prompts for the passphrase
```

`extract.py` prints a per-tab section and row count. If a tab's count drops, the
workbook's rows moved — fix the row numbers in `build/config.py`, which is the
only file that knows about spreadsheet layout.

Then commit `data.enc.json`. **Never commit `data.json` or the workbook** —
`.gitignore` covers both, but check `git status` before pushing.

To rotate the passphrase, re-run step 3 with a new one and redeploy. To generate
a strong one, `python3 build/encrypt.py --generate`.

## What's here

| Path | Purpose |
|---|---|
| `index.html` | The whole dashboard — one self-contained file |
| `data.enc.json` | Encrypted data (committed) |
| `build/config.py` | **Where the spreadsheet layout lives.** Edit this when the workbook changes |
| `build/extract.py` | Walks the config, emits `data.json`. No per-tab logic |
| `build/xlsxread.py` | Minimal stdlib .xlsx reader |
| `build/encrypt.py` | `data.json` → `data.enc.json` |
| `build/aesgcm.py` | Pure-Python AES-256-GCM (verified against NIST vectors) |
| `build/SCHEMA.md` | **The data contract.** Read before building anything that writes data |
| `build/PALETTE.md` | The chart palette and its accessibility validation |

## How this reads the data honestly

The workbook contains several traps that a naive dashboard would turn into
confident, wrong conclusions. The design choices below exist to prevent that,
and are worth preserving in any future version:

- **A `0` is not the same as "no data."** Four Formation blocks record zeros for
  2018–2024 because the metric did not exist yet. Plotted as zeros they produce
  spectacular fake growth in 2025. They are stored as `not_tracked` and drawn as
  a shaded "not tracked" band instead.
- **Lines never bridge a gap.** `spanGaps` is off everywhere, so a year nobody
  reported reads as missing rather than as a straight line through it.
- **Every figure is compared to 2019 as well as to last year.** COVID broke
  nearly every series; ASA went 22,153 → 11,771 → 18,740, and "up 4% on last
  year" and "down 18% on 2019" are both true.
- **Definitional breaks are plotted as separate series.** Safeguarding counted
  session attendance through 2023 and distinct individuals from 2024. Those are
  two series on one chart, never one line.
- **The Disaster tab is a table, not a chart.** Its columns mix calendar years
  with twelve-month periods ending 30 June, and the program changed purpose
  mid-series. Any trend line there would be fiction.
- **Coaching is a bar chart.** It is a single 2025 cross-section, not a series.
- **One axis, one unit, five series maximum.** A count is never plotted against
  a percentage, and charts cap at five series because only the palette's first
  five slots are verified distinguishable under colorblindness in every
  combination. See `build/PALETTE.md`.

All of the caveats are collected on the dashboard's own **Data Notes** page.

## Deploying

Push to GitHub, then Settings → Pages → deploy from `main` / root. The page is
static and self-contained apart from Chart.js on a CDN.

## Building the data-entry app later

`build/SCHEMA.md` is the contract. The dashboard reads `data.json` and nothing
else; `extract.py` is simply its first writer. An entry app that emits the same
shape needs no dashboard changes. Each series already carries `unit`, `format`,
and `owner` so per-department forms can be generated from the schema alone, and
every section has a stable `id` that must never be reused or renumbered.
