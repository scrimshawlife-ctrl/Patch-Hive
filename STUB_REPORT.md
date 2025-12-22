# STUB_REPORT

## P0 (runtime paths)
- `backend/ingest/modulargrid.py` — ModularGrid adapter boundary now fails closed via `ModularGridUnavailableError`. Action: kept as adapter-only interface (external implementation required).
- `patchhive/vision/gemini_interface.py` — `GeminiVisionClient.extract_rig` raises `NotImplementedError`. Action: kept as boundary adapter; core remains deterministic and requires an external overlay.

## P1 (dev/test infrastructure)
- `backend/core/abrexport.py` — TODO: add usage tracking. Action: left as-is (non-blocking analytics).
- `backend/core/ers.py` — TODO: async queue integration. Action: left as-is (sync executor remains default).
- `backend/tests/api/test_racks_api.py` — TODO: validation error serialization for 400 responses. Action: left as-is; xfail documents known bug.
- `backend/tests/README.md` — TODO: integration test folder. Action: left as-is.

## P2 (docs/examples)
- `backend/CATALOG_ARCHITECTURE.md` — sample `pass` placeholder. Action: left as-is (documentation pseudocode).
