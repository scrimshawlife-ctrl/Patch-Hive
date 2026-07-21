# Release notes — `v0.3.0-alpha.1`

**Tag:** `v0.3.0-alpha.1`  
**Target SHA:** main at tag time (post PR #82 hardening window)  
**Maturity:** **alpha** — incomplete toward production; not payment-enabled  
**Class:** development line `0.3.x` pre-release (VSI multi-photo + hygiene), not `1.0.0`

## Scope (included)

- Visual System Intelligence P0 contracts, inventory gate, multi-image evidence
- Multi-photo reconciliation + fusion confirm UX (user-initiated only)
- Rig revision picker / personal overlays; inventory receipt on RigDetail
- Module gallery search/filter; Cases/Patches list parity
- AI engineering foundation (just, telemetry, import guard)
- All default unit tests free of historical `patchhive` package imports
- Staging Compose profile + host plan (named host still operator-picked)

## Explicit non-claims

- Production deploy **not** performed  
- Live Stripe / production payments **disabled**  
- Vision production accuracy **NOT_COMPUTABLE**  
- Full dual-path rack router deletion **not** done  

## Operator notes

- Alembic head: `20240930_patch_user_overlays`
- Prefer `/api/canon/*` for exports/credits
- Staging: `docker compose -f docker-compose.staging.yml up -d --build`
- Gates: [OPERATIONS.md](../OPERATIONS.md), [ReleaseChecklist.md](../engineering/ReleaseChecklist.md)

## Upgrade

```bash
git fetch --tags
git checkout v0.3.0-alpha.1
# or pull main at the tagged commit
cd backend && alembic upgrade head
```
