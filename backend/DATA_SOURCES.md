# PatchHive Data Sources Documentation

**Last Updated**: 2026-07-21
**ABX-Core Version**: 1.3
**Database Schema Version**: 1.0

## Overview

This document provides complete provenance tracking for all data in the PatchHive database, in accordance with ABX-Core v1.3 SEED principles (no mystery data, full traceability).

## Data Sources

### 1. Eurorack Modules (32 modules)

**Source Type**: Manual curation from manufacturer specifications and ModularGrid community data
**Provenance**: `source="ModularGrid"`, `source_reference="https://www.modulargrid.net/"`
**Method**: Hand-curated from official manufacturer product pages and specifications
**Date Imported**: 2025-12-05
**Importer**: `integrations/modulargrid_importer.py`

#### Field-Level Provenance

| Field | Source | Trust Level | Notes |
|-------|--------|-------------|-------|
| `brand` | Manufacturer official | Direct | Standardized spelling |
| `name` | Manufacturer official | Direct | Exact product name |
| `hp` | Manufacturer specs | Direct | Width in HP units |
| `module_type` | Inferred from description | Inferred | VCO, VCF, VCA, ENV, LFO, SEQ, etc. |
| `power_12v_ma` | Manufacturer specs | Direct | +12V rail consumption |
| `power_neg12v_ma` | Manufacturer specs | Direct | -12V rail consumption |
| `power_5v_ma` | Manufacturer specs | Direct | +5V rail (when applicable) |
| `io_ports` | Manual mapping | Manual | Derived from manuals/specs |
| `tags` | Curated classification | Inferred | Based on functionality |
| `description` | Manufacturer copy | Direct | Product descriptions |
| `manufacturer_url` | Official website | Direct | Product page URLs |

#### Data Quality Notes

- **Power Specifications**: All values verified against official manufacturer datasheets
- **Missing Data**: Some older/discontinued modules may have incomplete power specs
- **I/O Ports**: Simplified representation; full patch diagrams would require additional schema
- **Module Types**: Primary categorization follows common Eurorack taxonomy (VCO, VCF, VCA, etc.)

### 2. Eurorack Cases (7 cases)

**Source Type**: Manual curation from manufacturer specifications
**Provenance**: `source="ModularGrid"`, `source_reference="https://www.modulargrid.net/"`
**Method**: Hand-curated from official manufacturer case specifications
**Date Imported**: 2025-12-05

#### Field-Level Provenance

| Field | Source | Trust Level | Notes |
|-------|--------|-------------|-------|
| `brand` | Manufacturer official | Direct | Case manufacturer |
| `name` | Manufacturer official | Direct | Product name |
| `total_hp` | Manufacturer specs | Direct | Total width in HP |
| `rows` | Manufacturer specs | Direct | Number of rows |
| `hp_per_row` | Manufacturer specs | Direct | HP distribution per row |
| `power_12v_ma` | Manufacturer specs | Direct | Total +12V capacity |
| `power_neg12v_ma` | Manufacturer specs | Direct | Total -12V capacity |
| `power_5v_ma` | Manufacturer specs | Direct | Total +5V capacity |
| `description` | Manufacturer copy | Direct | Product descriptions |
| `manufacturer_url` | Official website | Direct | Product page URLs |

### 3. Manufacturers (25 brands)

**Source Type**: Industry knowledge + manufacturer websites
**Method**: Curated list of major Eurorack manufacturers
**Storage**: Embedded in module records (normalized via brand field)

#### Manufacturer List

1. Mutable Instruments (France) - Now open-source
2. Make Noise (USA)
3. Intellijel (Canada)
4. Noise Engineering (USA)
5. Qu-Bit Electronix (USA)
6. 4ms Company (USA)
7. Doepfer (Germany) - Original Eurorack creator
8. ALM Busy Circuits (UK)
9. Mannequins (USA)
10. Hexinverter (Canada)
11. Befaco (Spain) - DIY focus
12. Erica Synths (Latvia)
13. Tiptop Audio (USA/China)
14. Malekko Heavy Industry (USA)
15. WMD (USA)
16. Joranalogue (Netherlands)
17. Xaoc Devices (Poland)
18. Industrial Music Electronics (USA)
19. Shakmat Modular (Belgium)
20. Instruo (UK)
21. Verbos Electronics (USA)
22. Synthesis Technology (USA)
23. Frequency Central (UK)
24. Random*Source (UK)
25. Buchla USA (USA)

### 4. Synth Catalog Research (Phase 2 seed)

**Source Type**: Sealed multi-source research packet (Abraxas skill `modular-synth-catalog-research`)  
**Provenance**: `source="SynthCatalogResearch"`, `source_reference="data/synth-catalog/seed-phase2-v1.json"`  
**Method**: Phase 1 brand index (~700+) + Phase 2 major-brand module tables, normalized into PatchHive catalog rows  
**Date Sealed**: 2026-07-21 (Abraxas PR #984)  
**Importer**: `integrations/synth_catalog_importer.py`  
**Seed**: `data/synth-catalog/seed-phase2-v1.json`  
**Policy packet**: `data/synth-catalog/seed-phase2-v1.sources.json`

#### What is admitted where

| Tier | Target table | Content |
|------|--------------|---------|
| Lightweight catalog | `module_catalog` | Phase 2 brand/name/category/availability; HP only when research recorded it (null otherwise) |
| Full specs | `modules` | Curated full-spec subset (power/I/O only when known; never invented) |

#### Field-Level Provenance

| Field | Source | Trust Level | Notes |
|-------|--------|-------------|-------|
| `brand` / `name` | Research Phase 2 tables | OBSERVED | Deduped by slug |
| `hp` | Research table when numeric | OBSERVED or null | Null when research used `—` / blank |
| `category` | Mapped from free-text research categories | Inferred | Taxonomy via `map_category()` |
| `is_available` | Research status column | OBSERVED | discontinued / available / upcoming |
| `power_*` / `io_ports` | Curated full-spec only | Direct when present | Null never filled with guesses |
| Brand index | Phase 1 ModularGrid manufacturer list reference | OBSERVED | Browse/filter support, not bulk scrape of modules |

#### Data Quality Notes

- **Not a ModularGrid dump**: Research used multi-source rotation (official, retailer, community) to avoid ToS bulk scrape
- **Sparse HP**: Most Phase 2 rows lack HP; catalog admits them for discovery; full rack placement still needs HP later
- **Idempotent**: Catalog skips existing slugs; full modules skip existing `(brand, name)` from any source
- **Rebuild**: `python3 scripts/build_synth_catalog_seed.py` (optional `--source-dir` to Abraxas skill references)

#### API

- `GET /api/synth-catalog/stats`
- `GET /api/synth-catalog/manufacturers`
- `POST /api/synth-catalog/import/catalog?dry_run=`
- `POST /api/synth-catalog/import/modules?dry_run=&clear_existing=`
- `POST /api/synth-catalog/import/all?dry_run=&clear_existing=`

## Data Collection Methodology

### Principles

1. **No Unauthorized Scraping**: All data manually curated from official sources
2. **ToS Compliance**: ModularGrid data used as reference only, not bulk scraped
3. **Manufacturer Permission**: Product specs are publicly available marketing material
4. **Community Standards**: Follows established Eurorack taxonomy and conventions

### Process

1. **Module Selection**: Focus on popular, widely-available modules
2. **Specification Verification**: Cross-reference multiple sources
3. **Standardization**: Normalize units (mA, HP, mm)
4. **Categorization**: Apply consistent module_type taxonomy
5. **Provenance Tagging**: Every record includes source metadata

### Validation

- Power specs verified against official datasheets
- HP widths confirmed from manufacturer specs
- Module types validated against common usage
- URLs checked for accuracy

## Known Gaps & Limitations

### Current Limitations

1. **Coverage**: 32 curated full-spec modules + Synth Catalog Research catalog expansion (~300+ browse rows; HP often null)
2. **I/O Details**: Simplified port representation; full signal flow not captured
3. **Firmware Versions**: Digital modules may have firmware variations not tracked
4. **Discontinued Modules**: Historical data may be incomplete
5. **Regional Variations**: Some modules have region-specific power requirements

### Future Expansion Opportunities

1. **User Contributions**: Allow community to submit verified module data
2. **Manufacturer APIs**: Direct integration where APIs are available
3. **ModularGrid Exports**: Support user-provided ModularGrid rack exports
4. **Enhanced I/O Modeling**: Detailed signal routing and normalization
5. **Firmware Tracking**: Version-specific feature sets for digital modules

## Data Integrity

### Deduplication Strategy

Modules are identified by composite key: `(brand, name)`
- Prevents duplicate entries on re-import
- Hash-based ID generation ensures stability

### Update Policy

- **New Modules**: Import via API or CLI
- **Corrections**: Update via API with provenance note
- **Deprecation**: Mark `is_discontinued` rather than delete
- **Versioning**: Module revisions tracked via name suffix (e.g. "Plaits v2")

## Compliance

### ABX-Core v1.3 SEED Enforcement

✅ **No Mock Data**: All modules are real, commercially available products
✅ **Full Provenance**: Every record has `source` and `source_reference`
✅ **Traceability**: Import timestamps and run_id tracked
✅ **Deterministic**: Same import files → same database state

### Legal Compliance

- Product specifications are publicly available facts (not copyrightable)
- URLs and descriptions used for informational purposes (fair use)
- No bulk scraping or ToS violations
- Manufacturers retain all rights to product names and trademarks

## Import History

### Initial Bootstrap (2025-12-05)

```
Run ID: 4c8f067f-8e32-49e4-bfc9-05882001b43f
Imported: 32 modules, 7 cases
Duration: ~2.5 seconds
Status: Success
```

**Provenance Metrics**:
- `imported_count`: 32 modules, 7 cases
- `skipped_count`: 0 (clean database)
- `total_processed`: 39 items

## Maintenance

### Adding New Modules

1. Add to `integrations/modulargrid_data.py`
2. Include all required fields with provenance
3. Run importer: `python -m integrations.modulargrid_importer`
4. Verify import via API: `GET /api/modules/`

### Data Quality Checks

- Monthly: Review for discontinued modules
- Quarterly: Update power specs for revised modules
- Annually: Full manufacturer catalog review

## Contact

For data corrections or additions:
- GitHub Issues: https://github.com/scrimshawlife-ctrl/Patch-Hive/issues
- Tag data submissions with: `data-quality` label

---

**Document Version**: 1.0
**Schema Version**: 1.0
**ABX-Core Compliance**: v1.3
