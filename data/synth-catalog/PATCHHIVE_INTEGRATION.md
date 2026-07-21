# Patch-Hive + Modular Synth Catalog Integration

**Date:** 2026-07-22  
**Status:** Analysis + Initial Integration Artifacts  
**Source Catalog:** User's completed research (767 brands, 29+ major detailed, full provenance, 20-source rotation)

## Executive Summary

PatchHive already has excellent architecture for a module catalog (see `backend/CATALOG_ARCHITECTURE.md` — two-tier: lightweight `module_catalog` + on-demand full `modules`).

Current data is very small (25 curated brands, 32 modules in `integrations/modulargrid_data.py`).

The completed synth catalog research provides:
- Phase 1: 767 brands (index)
- Phase 2: 29 major brands with detailed modules + tables
- Full provenance (OBSERVED/INFERRED + source rotation)
- Obsidian + JSON ready formats

**High-value integration**: Use the new catalog to bootstrap/populate PatchHive's `module_catalog` with high-quality, provenance-tagged data.

## Alignment with PatchHive

| PatchHive Concept       | Synth Catalog Match                  | Fit |
|-------------------------|--------------------------------------|-----|
| module_catalog (light)  | Phase 1 + Phase 2 brands + basic specs | Excellent |
| modules (full specs)    | Detailed Phase 2 entries             | Excellent |
| Provenance (ABX-Core)   | OBSERVED/INFERRED + rotation         | Excellent match |
| Canon / RigRevision     | Canonical DB + master catalog        | Natural |
| Integrations/           | New synth_catalog importer           | Direct |

## Recommended Integration Approach

### Phase A (Immediate)
1. Add `synth_catalog_data.py` (convert our structured data into PatchHive format).
2. Create `synth_catalog_importer.py` (or extend existing importer).
3. Copy `canonical_db.json` + key Markdown into `data/synth-catalog/`.
4. Update `DATA_SOURCES.md` with new source + provenance.

### Phase B
- Wire new data into catalog browsing APIs.
- Allow mixed sources (ModularGrid + Synth Catalog).
- Add "source" filter in catalog.

### Phase C (Later)
- Merge high-quality entries into main catalog.
- Use as primary seed for new users.

## Files Copied for Integration
- `imported-synth-catalog/master-catalog.md`
- `imported-synth-catalog/canonical_db.json`
- `imported-synth-catalog/phase2-major-brands.md`
- `imported-synth-catalog/phase1-brand-index.md`
- Full plan + rotation docs

## Next Concrete Steps (for execution)

1. Parse phase2 data into Python dicts matching MODULES_DATABASE format.
2. Generate a starter `synth_catalog_data.py`.
3. Add importer support.
4. Run in the backend with scrubbed verification.
5. Update docs.
6. Feature branch + full commit-and-merge ritual.

**Governance Notes:**
- All new data must carry provenance.
- Use 3-consecutive scrubbed runs for verification.
- Follow existing ABX-Core patterns.

---

**Status**: Ready to generate the data bridge and importer extension.

## Integration Execution Status (2026-07-22, Docker available)

### Changes Implemented
1. **Data + Importer**
   - backend/integrations/synth_catalog_data.py 
   - backend/integrations/synth_catalog_importer.py (style-matched)

2. **Router Additions**
   - synth-catalog endpoints added in router.py

3. **Bootstrap + Docs**
   - Import added, README extended

4. **Verification**
   - Local syntax: PASS
   - Docker db: healthy (port 5433)
   - Full make limited by temp clone env

Files ready for copy to real Patch-Hive checkout.
