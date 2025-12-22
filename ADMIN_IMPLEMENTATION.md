# ADMIN_IMPLEMENTATION

## Architecture
- **Admin API namespace**: `/api/admin/*` (FastAPI)
- **Role gating**: `Admin`/`Ops` for mutations; `Admin`/`Ops`/`Support`/`ReadOnly` for reads (`backend/admin/dependencies.py`)
- **Audit logging**: append-only `admin_audit_log` records for every admin mutation (`backend/admin/utils.py`)
- **No hard deletes**: modules are tombstoned; other entities are updated without removal.

## Models added/extended
- **users**: `display_name`, `role`, `referral_code`, `referred_by`
- **modules**: `status`, `replacement_module_id`, `deprecated_at`, `tombstoned_at`
- **admin_audit_log**: append-only audit log
- **gallery_revisions**: append-only revision table for admin approvals
- **runs**: minimal run tracking for rerun actions

## Routes
### Users
- `GET /api/admin/users?query=`
- `PATCH /api/admin/users/{user_id}/role`
- `PATCH /api/admin/users/{user_id}/avatar`
- `POST /api/admin/users/{user_id}/credits/grant`

### Modules
- `POST /api/admin/modules`
- `POST /api/admin/modules/import`
- `PATCH /api/admin/modules/{module_id}/status`
- `PATCH /api/admin/modules/{module_id}/merge`

### Gallery revisions
- `GET /api/admin/gallery/revisions?status=`
- `POST /api/admin/gallery/revisions/{revision_id}/approve`
- `POST /api/admin/gallery/revisions/{revision_id}/confirm`

### Runs / Exports / Cache
- `GET /api/admin/runs?status=`
- `POST /api/admin/runs/{rig_id}/rerun`
- `POST /api/admin/exports/{export_id}/unlock`
- `POST /api/admin/exports/{export_id}/revoke`
- `POST /api/admin/cache/invalidate`

### Leaderboards
- `GET /api/admin/leaderboards/modules/popular`
- `GET /api/admin/leaderboards/modules/trending?window_days=`
- `GET /api/admin/leaderboards/categories/exported`

## Frontend admin console
- `/admin` dashboard and subpages for users, modules, gallery, runs, exports, leaderboards.
- Access gated by role in the UI, with server-side enforcement in admin routes.

## How to run
1. Apply migrations: `alembic upgrade head`
2. Start backend: `uvicorn main:app --reload`
3. Start frontend: `npm install && npm run dev`
4. Login with an Admin/Ops role to access `/admin`.
