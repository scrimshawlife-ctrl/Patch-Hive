# Design Engine staging enablement receipt

```yaml
date: "2026-07-26"
method: scripts/staging/design-engine.ps1
compose:
  - docker-compose.staging.yml
  - docker-compose.staging.design-engine.yml
api: http://localhost:18000
result: PASS
payments:
  STRIPE_TEST_MODE: true
  ALLOW_PRODUCTION_PAYMENTS: false
flags:
  ENABLE_PATCHBOOK_DESIGN_ENGINE: true
  ENABLE_CANON_EXPORT_FULFILLMENT: true
  ENABLE_INLINE_EXPORT_FULFILLMENT: true
  ENABLE_PATCHBOOK_PUBLICATION_PROFILE: false
```

## Procedure

1. Compose up backend with design-engine overlay (flags + `exports` volume).  
2. `GET /health/ready` → healthy.  
3. Seed golden demo into live staging DB; ensure admin.  
4. `POST /api/canon/exports/preview` (free) → style_recipe_hash + page_summaries.  
5. `POST /api/canon/style-recipes` → library recipe.  
6. Admin grant credits.  
7. `POST /api/canon/exports` with recipe → **status=succeeded** + pack hashes.  
8. Pack directory under `/app/exports/design_packs/<export_id>/`.

## OBSERVED

| Step | Result |
|------|--------|
| Preview | PASS (`load_path=compile_on_export`, 3 page summaries) |
| Style recipe save | PASS |
| Credit grant | PASS |
| Export + inline fulfill | PASS `status=succeeded` |
| `pack_manifest_hash` / `composition_hash` | present |
| Example export_id | `export-056633944bb86ac11db1464c` |

## Re-run

```powershell
powershell -File scripts/staging/design-engine.ps1
```

**Authority:** local staging only; not production flag flip; payments remain fail-closed.
