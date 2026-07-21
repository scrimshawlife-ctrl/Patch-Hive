# SYSTEM_CONTEXT (token-compressed)

REPO=PatchHive | GOAL=rig inventory→deterministic patches→PatchBook export | NOT=audio_DSP|hardware_control|live_payments_default

STACK=FastAPI+SQLAlchemy+Alembic+Postgres | FE=React+Vite+TS | TEST=pytest+vitest+playwright | TASK=just+make

ENTRY=backend/main.py,frontend/src/App.tsx | CANON=backend/canon | VISION=backend/evidence | GEN=backend/patches+inventory_gate | BRIDGE=runs/bridge native_ids

HIER=User>Rig>RigRevision>Run>PatchLibrary>Patch | TRUST=image→evidence→confirm→inventory→generate | NO_SELF_CONFIRM

API=/api/{modules,cases,racks,patches,runs,canon/*,export/*} + /api/racks/{id}/evidence/* + auth /api/community/auth

FLAGS=legacy_social/publish/leaderboards off | STRIPE_TEST=true | ALLOW_PROD_PAY=false

DOCS=CURRENT_STATE,CONTINUATION,CANON,VSI,PRODUCTION_READINESS | ENG=docs/engineering/* | AI=AI_CONTEXT,SYSTEM_CONTEXT

IDX=.codebase-memory/{symbols/tags,graph/module_graph.json,summaries/*} | regen=just memory | gitignore indexes

CMD_BE="cd backend && pytest tests --ignore=tests/acceptance -q" | CMD_FE="cd frontend && npm test -- --run && npm run type-check" | CMD_VAL=just validate

ALEMBIC=20240929_visual_inventory_evidence | IDS=rig-rev-{hash},gen-run-{id}-{hash} | AUDIO_WORD=port_metadata_only

RULES=fail_closed;NOT_COMPUTABLE>invent;no_prod_deploy_without_authority;dual_path_slice_not_bigbang;CI_authoritative_if_no_docker
