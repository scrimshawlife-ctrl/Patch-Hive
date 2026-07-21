# Vision evaluation fixtures

**License:** synthetic internal fixtures only — not a production dataset.  
**Version:** `vision-eval.v1`

## Purpose

Provide a **deterministic** evaluation harness for CI:

- module detection precision/recall when labels exist
- explicit `NOT_COMPUTABLE` for production accuracy metrics

Do **not** publish fixture scores as product accuracy.

## Layout

```text
manifest.json
<sample_id>/
  image.bin          # bytes fed to VisionProviderContext
  labels.json        # ground truth modules/manufacturers
  recorded_packet.json  # optional fixture provider packet
```

## Run

```bash
cd backend
env -u PYTHONPATH python -m pytest tests/unit/test_vision_evaluation.py -q
```
