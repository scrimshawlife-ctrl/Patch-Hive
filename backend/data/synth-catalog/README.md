# Packaged synth-catalog seed (backend image)

Copy of repo `data/synth-catalog/seed-phase2-v1.json` for Docker/Render
layouts that only ship the `backend/` tree (`WORKDIR /app`).

Canonical research artifacts and receipts remain under repo-root
`data/synth-catalog/`. Rebuild both with:

```bash
python3 scripts/build_synth_catalog_seed.py
# then: cp data/synth-catalog/seed-phase2-v1*.json backend/data/synth-catalog/
```
