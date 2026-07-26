#!/usr/bin/env bash
# PatchHive local staging smoke (Linux/macOS)
# See scripts/staging/smoke.ps1 for Windows.
set -euo pipefail

API_PORT="${STAGING_API_PORT:-18000}"
FE_PORT="${STAGING_FE_PORT:-15173}"
DB_PORT="${STAGING_DB_PORT:-5433}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.staging.yml}"
SKIP_BUILD="${SKIP_BUILD:-0}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export STAGING_API_PORT="$API_PORT"
export STAGING_FE_PORT="$FE_PORT"
export STAGING_DB_PORT="$DB_PORT"
export STAGING_PUBLIC_API_URL="http://localhost:${API_PORT}"
export STAGING_CORS_ORIGINS="http://localhost:${FE_PORT},http://localhost:5173,http://localhost:3000"
export STAGING_SECRET_KEY="${STAGING_SECRET_KEY:-staging-smoke-secret-key-min-32-chars-xx}"
export STAGING_DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"

compose() { docker compose -f "$COMPOSE_FILE" "$@"; }

echo "=== Staging smoke (API :${API_PORT} FE :${FE_PORT} DB :${DB_PORT}) ==="
if [[ "$SKIP_BUILD" == "1" ]]; then
  compose up -d
else
  compose up -d --build
fi

ready_url="http://localhost:${API_PORT}/health/ready"
for i in $(seq 1 45); do
  if curl -sf "$ready_url" >/tmp/ph-ready.json; then
    echo "GET /health/ready -> $(cat /tmp/ph-ready.json)"
    break
  fi
  echo "  wait ready $i..."
  sleep 2
  if [[ "$i" -eq 45 ]]; then
    echo "ready probe failed" >&2
    exit 1
  fi
done

echo "GET /health -> $(curl -sf "http://localhost:${API_PORT}/health")"
current="$(compose exec -T backend python -m alembic current)"
echo "alembic current: $current"
echo "$current" | grep -q "20260726_module_registry_slugs" || {
  echo "unexpected alembic head" >&2
  exit 1
}

mkdir -p tmp/staging-smoke
compose exec -T db pg_dump -U patchhive -d patchhive -Fc -f /tmp/patchhive.dump
docker compose -f "$COMPOSE_FILE" cp db:/tmp/patchhive.dump tmp/staging-smoke/patchhive-staging.dump
compose exec -T db pg_restore -l /tmp/patchhive.dump | grep -q TABLE
compose exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS patchhive_restore_smoke;"
compose exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE patchhive_restore_smoke;"
compose exec -T db pg_restore -U patchhive -d patchhive_restore_smoke --no-owner --no-acl /tmp/patchhive.dump
ver="$(compose exec -T db psql -U patchhive -d patchhive_restore_smoke -t -A -c "SELECT version_num FROM alembic_version;")"
echo "restored alembic_version: $ver"
echo "$ver" | grep -q "20260726_module_registry_slugs" || exit 1
compose exec -T db psql -U patchhive -d postgres -c "DROP DATABASE IF EXISTS patchhive_restore_smoke;"

echo "SMOKE PASS"
echo "  Ready: $ready_url"
echo "  Head:  20260726_module_registry_slugs"
