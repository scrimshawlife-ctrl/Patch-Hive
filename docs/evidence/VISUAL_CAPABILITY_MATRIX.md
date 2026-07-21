# Visual system intelligence — capability matrix

**Baseline SHA:** `2b72d5b10fef1ab70c74d3c40379eb1593cf8293`  
**Head (this campaign):** see PR / CURRENT_STATE after merge  
**Date:** 2026-07-21

| capability | status | source_files | tests | documentation | blocking_gaps |
|---|---|---|---|---|---|
| secure image upload validation | IMPLEMENTED | `backend/evidence/images.py` | `test_image_evidence.py` | SECURITY, VSI | production AV scanner still adapter-only |
| image re-encode + EXIF strip | IMPLEMENTED | `evidence/images.py` | unit | SECURITY | retention policy product copy |
| local image quality gates | PARTIAL | `assess_local_image_quality` | `test_vision_provider_and_quality.py` | VSI roadmap WS1 | provider blur/glare scores not calibrated |
| photo evidence UI review | PARTIAL | `frontend/src/pages/RackBuilder.tsx` | e2e partial | VSI | no multi-photo; limited overlay |
| provider-neutral vision adapter | IMPLEMENTED | `evidence/vision_provider.py` | unit | VSI, ARCHITECTURE | no live cloud/local model adapter |
| mock/fixture vision providers | IMPLEMENTED | mock + recorded fixture | unit | VSI roadmap | eval dataset NOT_COMPUTABLE |
| module candidate detection | PARTIAL / STUB | mock devices; `canon/runes.detect_modules`; historical Gemini stubs | unit | VSI | real detection + registry retrieval |
| manufacturer/model resolution | PARTIAL | `runes.resolve_modules` gallery match | existing unit/compiler | VSI | confidence calibration missing |
| confirmation workflow | PARTIAL | RackBuilder buttons; `ConfirmationDecision` contracts; admin gallery confirm | unit + UI smoke | VSI | full hybrid multi-candidate API |
| immutable inventory revision | IMPLEMENTED (in-process) | `canon/inventory.py`, `visual_contracts.py` | unit | DATA_MODEL | Alembic persistence follow-on |
| system capability graph | IMPLEMENTED (in-process) | `build_system_capability_graph` | unit | DATA_MODEL | port-level registry completeness |
| confirmed-hardware patch generation gate | IMPLEMENTED | `enforce_confirmed_inventory_constraints` | unit | PATCH_ENGINE, VSI | wire into live generate route |
| cable endpoint inference | STUB | mock returns empty; ConnectionCandidate contract | unit (occlusion rule) | VSI §7 | P1 model + UX |
| patch validation | IMPLEMENTED | `canon/compiler.validate_patch_graph` | unit | PATCH_ENGINE | inventory gate wiring |
| Patch Book one-page compiler | SPEC_ONLY / PARTIAL | export/pdf, patchbook packages | patchbook tests | PATCH_BOOK_GENERATOR | full page-fit 0.3.x |
| deterministic SVG/PDF/JSON/ZIP | PARTIAL | export routes | unit/api | EXPORT docs | manifest completeness |
| provenance retention | PARTIAL | EvidenceRecord, ProviderReceipt, Provenance | unit | CANON | image retention product policy |
| multi-photo reconciliation | MISSING | — | — | VSI roadmap WS6 | P1 |
| evaluation metrics dataset | NOT_COMPUTABLE | — | — | VSI §12 | licensed dataset required |

## Gap priority (execution)

### P0 remaining after this campaign

1. Wire inventory constraint gate into `POST /api/patches/generate` (and canon compiler entry).
2. Persist `SystemInventoryRevision` via Alembic when product path is ready.
3. Authenticated upload endpoint with retention/consent flags (policy-backed).
4. End-to-end confirmation API for hybrid photo/manual inventory.

### P1

Multi-photo, layout, ports/controls, cables, photo-derived Patch Books, calibration.

### P2

Live camera, marketplace, community system matching — do not promote ahead of P0.
