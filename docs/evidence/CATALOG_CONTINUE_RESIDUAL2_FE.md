# Catalog continue — residual-2 power + FE filters (2026-07-22)

## Residual power (round 2)

Aggressive MG URL map + passive detection (`passive` / multiples / blanks with 0 mA).

| Metric | Value |
|--------|------:|
| Still null before | 61 |
| Found this round | **29** |
| With +12 applied (incl. passive 0) | 16+ |
| ModuleCatalog +12 after | **354 / 399 (88.7%)** |
| Remaining null +12 | **45** |

Overlay: `data/synth-catalog/overlays/module-power-depth-v3.json`  
Results: `hermes-research/power-depth-residual-2-results.json`  
Bootstrap updated to apply v3 after v1/v2.

Passive 0 mA only when page text indicates passive/unpowered multiples/blanks (OBSERVED), not invented for all blanks.

## Case rails

| Case | Action |
|------|--------|
| Happy Ending Kit | **No case rail capacity** — microZEUS is a module PSU; leave null fail-closed |
| 4ms Pod* | Research: rail current unspecified; leave null |
| NiftyCASE / LC3 | Already filled earlier |

## FE

Modules gallery filters (API already supported):

- **Source** (`?source=`) from stats `by_source`
- **Status** (`?is_available=`) including `duplicate`, `non_eurorack`, `desktop`, `unresolved`

## Place-loop

LC3 / Mantis power headroom still **verified** after residual-2.

## Residual 45

Mostly: vintage Befaco pages 404, Cwejman, expanders without draw, blanks without MG passive text, some Intellijel/Joranalogue slug gaps. Leave fail-closed.
