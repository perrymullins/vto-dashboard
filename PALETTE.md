# EDOT chart palette

Derived for this dashboard from the EDOT brand hues (navy `#1b2a4a`, gold
`#c9a227`, crimson `#9e1b32`) and validated with the data-viz six checks.
Do not hand-edit these hexes — re-derive and re-validate if they must change.

## Categorical slots

| Slot | Hue | Light (`#ffffff`) | Dark (`#141c2e`) |
|---|---|---|---|
| 1 | blue | `#3750be` | `#4863c6` |
| 2 | green | `#0f7805` | `#397b33` |
| 3 | ocean | `#0a91cd` | `#039fe1` |
| 4 | gold | `#968c00` | `#9f962a` |
| 5 | rose | `#962369` | `#b73c84` |
| 6 | orange | `#d25f19` | `#e76300` |
| 7 | purple | `#9164d2` | `#8d57d5` |
| 8 | crimson | `#af321e` | `#c03f2a` |

## Validation results

Run:

```
python3 scripts/validate_palette.py \
  "#3750be,#0f7805,#0a91cd,#968c00,#962369,#d25f19,#9164d2,#af321e" \
  --mode light --surface "#ffffff"
python3 scripts/validate_palette.py \
  "#4863c6,#397b33,#039fe1,#9f962a,#b73c84,#e76300,#8d57d5,#c03f2a" \
  --mode dark --surface "#141c2e"
```

| Check | Light | Dark |
|---|---|---|
| Lightness band | PASS (8/8) | PASS (8/8) |
| Chroma floor | PASS (8/8) | PASS (8/8) |
| CVD separation, adjacent | PASS ΔE 21.9 | PASS ΔE 17.8 |
| Normal-vision floor, adjacent | PASS ΔE 22.1 | PASS ΔE 20.1 |
| Contrast vs surface | PASS, all ≥ 3:1 | PASS, all ≥ 3:1 |

**All-pairs safety: the first five slots.** Validated with `--pairs all` in both
modes (worst CVD ΔE 9.5 light / 9.8 dark; worst normal ΔE 16.5 / 15.8). The
reference palette manages three; this one manages five because the search
optimized for prefix depth rather than adjacency alone.

That matters because slots are assigned in order, so an N-series chart puts
slots 1..N on screen together — the *prefix* is the set that actually co-occurs,
not just neighbouring pairs. **Charts therefore cap at five simultaneous
series.** Sections with more (Population's 12, Diocesan Council's 13) default to
their headline series and let the reader add up to four more; the full data
stays in the table under every card.

No slot needs the sub-3:1 relief rule — every step clears 3:1 against its
surface in both modes.

## Other roles

| Role | Light | Dark |
|---|---|---|
| Chart surface | `#ffffff` | `#141c2e` |
| Page plane | `#f4f6fa` | `#0d1422` |
| Primary ink | `#1d2433` | `#eef1f7` |
| Secondary ink | `#4a5468` | `#aeb9d4` |
| Muted (axis/labels) | `#6b7385` | `#8895b3` |
| Gridline | `#e6e9f0` | `#22304d` |
| Baseline / axis | `#cbd2e0` | `#33415f` |
| Delta good | `#1f6b4a` | `#4aa87d` |
| Delta bad | `#9e1b32` | `#e0687c` |
| Not-tracked band | `rgba(107,115,133,.10)` | `rgba(174,185,212,.10)` |

Status colors keep the brand's own: good `#2e7d5b`, bad `#b23a48`, and each
ships with a label, never color alone.

## Sequential ramp

Single hue, brand blue, light→dark — for the school-enrollment heat table only:

`#e2e9f7` `#c4d2ef` `#9db3e2` `#7593d4` `#4e73c6` `#3750be` `#2a3f92` `#1d2c66`
