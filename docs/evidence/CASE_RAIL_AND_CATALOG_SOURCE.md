# Case rail enrichment + module_catalog.source (2026-07-22)

## 1. Case rail capacity (priority for place-loop headroom)

### Applied (fill-null only)

| Case | +12 mA | −12 mA | +5 mA | Provenance |
|------|-------:|-------:|------:|------------|
| **Doepfer A-100LC3** | 2000 | 1200 | 4000 | PSU3 common ratings already used for A-100LC1/LC6/P6 siblings in the same research pack (`Cases4PatchHive`); LC3 previously only had free-text PSU note without numeric rails |
| **Cre8audio NiftyCASE** | 1500 | 500 | 500 | **OBSERVED** official product page `cre8audio.com/niftycase` peak bus currents (2026-07-22) |

Updated surfaces:

- Staging `cases` + `case_power_systems`
- `fixtures/cases_research_2026.json`
- `data/cases/seed-v1.json`

### Deferred (still null — fail-closed)

- Tiptop Happy Ending Kit (adapter mA only; microZEUS rail split not OBSERVED)
- 4ms Pod* (research: rail current unspecified)
- Erica travel cases, several Pittsburgh/Buchla boats without numeric rails

### Place-loop recheck (rack id 4, case A-100LC3)

| Rail | Draw | Capacity | Headroom | Status |
|------|-----:|---------:|---------:|--------|
| +12V | 369 | 2000 | 1631 | **verified** |
| −12V | 131 | 1200 | 1069 | **verified** |
| +5V | 0 | 4000 | 4000 | **verified** |

Module-level missing-power warnings: **none**.  
Case `POWER_UNSPECIFIED` advisory: **gone** for LC3 place-loop.

Receipts:

- `data/synth-catalog/receipts/case-rail-enrichment-staging-apply.json`
- `data/synth-catalog/receipts/place-loop-case-rail-recheck.json`

## 2. `module_catalog.source` column

| Piece | Detail |
|-------|--------|
| Migration | `20260722_module_catalog_source` |
| Column | `module_catalog.source` `String(50)` nullable + index |
| Backfill | Existing rows → `SynthCatalogResearch` |
| Importer | Sets `source` from seed row or default `SOURCE_NAME` |
| Populator | ModularGrid → `ModularGrid` / CSV → `ModularGridCSV` |
| Browse API | `?source=` filter; sort by `source` |
| Stats | `by_source` breakdown |
| Materialize | `source_reference` includes catalog source when present |

### Staging after migration

| Metric | Value |
|--------|------:|
| `module_catalog` rows | 408 |
| `source=SynthCatalogResearch` | 408 |
| null source | 0 |

Receipt: `data/synth-catalog/receipts/module-catalog-source-column.json`

## Tests

- `test_catalog_source_persisted_and_filterable`
- `test_import_catalog_idempotent` asserts research source on import
