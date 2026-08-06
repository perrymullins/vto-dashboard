# `data.json` Schema — v1

This file is the contract between data producers and the dashboard.

The dashboard reads **only** `data.json`. It never touches the spreadsheet. Today
`extract.py` is the only writer. A future data-entry app becomes a second writer;
as long as it emits this shape, the dashboard needs no changes.

## Top level

```json
{
  "meta":     { ... },
  "themes":   [ ... ],
  "sections": [ ... ]
}
```

### `meta`

| Field | Type | Notes |
|---|---|---|
| `schemaVersion` | int | `1`. Bump on breaking change; dashboard asserts it. |
| `generated` | ISO 8601 date | When this file was produced. |
| `source` | string | Filename of the source workbook, or `"data-entry-app"`. |
| `reportingYear` | int | The VTO cycle this file supports (e.g. `2026`). |
| `latestDataYear` | int | Most recent year with real values. Drives "current" KPIs. |
| `baselineYear` | int | Pre-COVID comparison anchor. `2019`. |

### `themes`

Display grouping for navigation. Order here is nav order.

```json
{ "id": "growth", "label": "Congregational Growth",
  "blurb": "ASA, size-tier movement, and community counts.",
  "sections": ["communities.asa", "communities.growth_1plus"] }
```

`sections` lists section IDs in display order. A section ID must appear in
exactly one theme.

### `sections`

One entry per metric block. This is the unit of both display (a card) and
future data entry (a form).

```json
{
  "id": "communities.asa",
  "tab": "Communities",
  "theme": "growth",
  "title": "EDOT Average Sunday Attendance",
  "subtitle": "as reported 12/31 of previous year",
  "kind": "timeseries",
  "periodType": "year",
  "trackingStart": null,
  "owner": "CMV",
  "series": [ ... ],
  "rows": [ ... ],
  "notes": [ "..." ],
  "caveats": [ ... ]
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable, `tab.slug`. **Never renumber or reuse.** The entry app addresses metrics by this. |
| `tab` | string | Source worksheet name. Preserved so workbook users can find the original. |
| `theme` | string | Theme ID. Redundant with `themes[].sections` for convenience. |
| `title` | string | Card heading. |
| `subtitle` | string \| null | Methodology line, e.g. "based on prior year's parochial report". |
| `kind` | enum | `timeseries` \| `categorical` \| `matrix` \| `irregular`. See below. |
| `periodType` | enum | `year` \| `schoolYear` \| `custom`. |
| `trackingStart` | string \| null | First period with real collection. Earlier periods render as "not tracked" regardless of stored value. **This is how false zeros are neutralized.** |
| `owner` | string \| null | Department/person initials from the workbook (e.g. `TL`, `AG`, `KBD`). Drives future entry-form routing. |
| `series` | array | Column definitions. |
| `rows` | array | Period-keyed observations. |
| `notes` | string[] | Free-text footnotes for the whole block. |
| `caveats` | array | Structured, period-scoped warnings. |

### `kind`

| Value | Meaning | Rendering |
|---|---|---|
| `timeseries` | Rows are periods, ordered. The common case. | Line chart |
| `categorical` | Rows are categories, **not** time. E.g. Coaching 2025 activity types. | Bar chart. **Must never be drawn as a trend.** |
| `matrix` | Rows are entities, series are periods. E.g. schools × school-years. | Sortable table + sparklines |
| `irregular` | Periods overlap or are non-comparable. E.g. Disaster. | Annotated table only, no trend line |

### `series[]`

```json
{ "id": "asa", "label": "ASA", "unit": "count",
  "format": "integer", "higherIsBetter": true, "owner": "CMV" }
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable key used in `rows[].values`. |
| `label` | string | Column/legend text. |
| `unit` | enum | `count` \| `percent` \| `usd` \| `ratio`. |
| `format` | enum | `integer` \| `percent1` \| `percent0` \| `usd0` \| `usd2` \| `decimal1`. |
| `higherIsBetter` | bool \| null | Colors YoY deltas green/red. `null` = neutral, no coloring. |
| `owner` | string \| null | Overrides section `owner` when a single block spans departments. |

`unit` and `format` exist so a future entry form can pick the right input type
and validation with no extra config.

### `rows[]`

```json
{ "period": "2025", "values": { "asa": 18740 }, "note": null }
```

`period` is a string, not a number — `"2024-2025"` and `"12 mos. ending 2022-06-30"`
are both valid. For `periodType: "year"` it is a 4-digit year string.

### Value states — the important part

A value in `rows[].values` is one of:

| State | Encoding | Meaning | Dashboard behavior |
|---|---|---|---|
| Number | `18740` | Real measurement | Plot it |
| True zero | `0` | Genuinely zero, and we know it | Plot at zero |
| Missing | `null` | Not reported this period | **Break the line. Never interpolate.** |
| Not tracked | `{"state":"not_tracked","raw":"Not recorded"}` | Metric didn't exist / wasn't collected | Dimmed band, labeled. Excluded from trend math. |
| Dirty | `{"value":34,"raw":"34* (10)","note":"10 churches ..."}` | Parsed a number out of messy text | Plot `value`, show ⓘ with `raw` |

Rule: **`0` and `null` mean different things and must never be conflated.**
A `0` that really means "we hadn't started counting" belongs behind
`trackingStart`, or as `not_tracked` — not as a plotted zero.

### `caveats[]`

```json
{ "period": "2021", "type": "methodology",
  "text": "Represents only up until March 8, 2020" }
```

`type` is one of `methodology` (counting changed), `coverage` (partial data),
`covid` (pandemic disruption), `definition` (what's counted changed),
`estimate` (value is estimated). `period` may be `null` for block-wide caveats.

Every caveat is aggregated into the dashboard's Data Notes page.

## Rules for any writer

1. `id` values are permanent. Renaming a metric changes `title`, never `id`.
2. Never emit `0` for "we didn't measure this." Use `null` or `not_tracked`.
3. Percentages are stored as fractions (`0.575`), not `57.5`.
4. Currency is stored in dollars as a number, unrounded.
5. Preserve the original cell text in `raw` whenever parsing was lossy.
6. Never drop a footnote. If it doesn't fit `caveats`, put it in `notes`.
