# ABX_RUNES_REPORT

## Status
- Added ABX-Runes spine under `backend/patchhive/runes/` (manifest, schema, registry, assets).
- Manifest enforces deterministic rune IDs and maps core handlers to rune entries.

## Files Added
- `backend/patchhive/runes/manifest.json`
- `backend/patchhive/runes/schema.py`
- `backend/patchhive/runes/registry.py`
- `backend/patchhive/runes/assets/*.svg`
- `backend/patchhive/runes/tests/test_manifest.py`

## Core Handlers Mapped
- `patches.engine:build_rack_state_ir`
- `patches.engine:generate_patches_for_rack`
- `patches.engine:generate_patches_with_ir`
- `patchhive.ops.build_canonical_rig:build_canonical_rig`
- `patchhive.gallery.revisions:append_revision`
- `integrations.modulargrid_importer:import_all`
- `export.pdf:generate_patch_pdf`
- `export.pdf:generate_rack_pdf`
- `export.visualization:generate_patch_diagram_svg`
- `export.visualization:generate_rack_layout_svg`
- `export.waveform:generate_waveform_svg`

## Validation
- Deterministic rune_id rule: `sha256("patchhive:" + maps_to + ":" + name)[:16]`
- Enforces:
  - unique rune IDs
  - importable handler paths
  - asset existence
  - no orphan assets
  - no unmapped core handlers

## Commands
- Validate manifest (Python):
  - `python -c "from patchhive.runes.registry import validate_manifest; print(validate_manifest())"`
- Run rune tests (pytest):
  - `pytest patchhive/runes/tests/test_manifest.py`
