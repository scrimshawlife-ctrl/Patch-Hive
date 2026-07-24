# Catalog Seeding + Registry Wiring (2026-07-23)

**Status:** Complete for this phase.

## Actions
- Seeded `module_catalog` with 376 rows from `data/synth-catalog/seed-phase2-v1.json` (`catalog_modules`).
- All rows wired with `registry_manufacturer_slug` + `registry_device_slug` (improved fuzzy matching in seeder).
- Updated `ModuleCatalog.to_dict()` to expose the registry links.
- Wired into materialization:
  - `materialize_catalog_entry` now copies registry slugs when creating full `Module`.
  - Return payloads (both "exists" and "created") include the links.
- Improved seeder matching logic.
- Added `tests/unit/test_catalog_materialize_registry.py` (passes).
- Small frontend enhancement in Registry explorer to surface links.

## Verification
- Catalog total: 376, 376 with reg_man links, many with dev links.
- Materialize test: passes and carries links (e.g. acid-rain-technology-junction → acid-rain-technology).
- API `/api/modules/catalog` returns registry fields.
- Only 1 full Module materialized so far (on-demand; more will appear as users place modules).

## Next
- Seed full_spec_modules for richer initial Modules (power/io).
- Expand Modules.tsx / catalog UI to show "linked in Registry" badges + links.
- When materializing, optionally pull more data from DeviceModel/Revision (ports, controls).
- Property tests or more coverage for catalog ↔ registry roundtrips.

See also: PDB_EXPLORER_WIRING_20260723.md, PDB_DB_SEED_20260723.md
