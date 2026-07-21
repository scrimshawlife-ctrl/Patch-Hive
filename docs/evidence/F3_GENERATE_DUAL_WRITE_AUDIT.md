# F3 — Generate dual-write audit

**Date:** 2026-07-21  
**Baseline:** main @ pre-merge of this PR  
**Slice:** dual-path residual **F3** ([DUAL_PATH_RETIREMENT_DESIGN.md](DUAL_PATH_RETIREMENT_DESIGN.md))  
**Authority:** OBSERVED tests; no production deploy  

## Intent

Prove `POST /api/patches/generate/{rack_id}` dual-writes:

1. **Native export bridge** — `rig-rev-*`, `gen-run-*`, 64-char manifest, `export_bridge_ready`  
2. **Sealed inventory revision** — `SystemInventoryRevisionRecord` + response `inventory_revision_id`  
3. **Fail closed** — empty inventory → `generation_status=NOT_COMPUTABLE`, zero patches, **still** bridge+inventory rows  
4. **No invent** — response never contains `legacy-rack-*` / `legacy-run-*` when rack exists  

## Path (OBSERVED)

```text
POST /api/patches/generate/{rack_id}
  → Run (integer) create
  → ensure_legacy_run_export_bridge  # name historical; IDs native
       → RigRevisionRecord (rig-rev-{content[:32]})
       → GenerationRunRecord (gen-run-{run_id}-{content[:16]})
       → PatchLibraryRecord (library-{source_run_id})
  → forbid legacy-* ids when export_bridge_ready
  → generate_patches_with_ir
       → evaluate_rack_inventory_gate (placements → USER_CONFIRMED)
       → persist_system_inventory_revision
       → patches or empty NOT_COMPUTABLE
  → response: bridge fields + inventory_revision_id + gate code + generation_status
```

## Tests

| Test | File | Asserts |
|------|------|---------|
| Happy path dual-write | `tests/api/test_generate_bridge.py` | native IDs, inv row, library, list run parity |
| Empty rack | same | NOT_COMPUTABLE, still bridge + inv |
| Stable rig-rev | same | two generates → same `rig_revision_id`, different `source_run_id` |
| Unit gate | `tests/unit/test_inventory_gate.py` | already covered |

## Decision

| Claim | Status |
|-------|--------|
| Generate mints only native bridge IDs for known racks | **PASS** |
| Generate persists inventory revision | **PASS** |
| Empty rack fail-closed with dual-write | **PASS** |
| Racks router deletion | **NOT_IN_SCOPE** (F3) |

## Residual (not F3)

- Evidence-confirmed inventory vs placement inventory still dual vocabulary (product OK)  
- FE may call generate without sealed evidence inventory (server uses placements)  
- F2/F4 canon/rigs aliases deferred  
