#!/usr/bin/env bash
# Design Engine staging enablement walkthrough (local compose).
# Turns on design flags via compose overlay, seeds golden demo, runs API preview+export.
#
# Usage (repo root):
#   bash scripts/staging/design-engine.sh
#   SKIP_BUILD=1 bash scripts/staging/design-engine.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

API_PORT="${STAGING_API_PORT:-18000}"
FE_PORT="${STAGING_FE_PORT:-15173}"
DB_PORT="${STAGING_DB_PORT:-5433}"
DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"
SKIP_BUILD="${SKIP_BUILD:-0}"
COMPOSE_BASE="${COMPOSE_BASE:-docker-compose.staging.yml}"
COMPOSE_DESIGN="${COMPOSE_DESIGN:-docker-compose.staging.design-engine.yml}"

export STAGING_API_PORT="$API_PORT"
export STAGING_FE_PORT="$FE_PORT"
export STAGING_DB_PORT="$DB_PORT"
export STAGING_DB_PASSWORD="$DB_PASSWORD"
export STAGING_PUBLIC_API_URL="http://localhost:${API_PORT}"
export STAGING_CORS_ORIGINS="http://localhost:${FE_PORT},http://localhost:5173"
export STAGING_SECRET_KEY="${STAGING_SECRET_KEY:-staging-smoke-secret-key-min-32-chars-xx}"

if ! docker version >/dev/null 2>&1; then
  echo "Docker engine not available" >&2
  exit 1
fi

compose() { docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_DESIGN" "$@"; }

echo "=== Design Engine staging (API :${API_PORT}) ==="
if [[ "$SKIP_BUILD" == "1" ]]; then
  compose up -d backend || { compose up -d db; compose up -d backend; }
else
  compose up -d --build backend || { compose up -d db; compose up -d --build backend; }
fi

ready_url="http://localhost:${API_PORT}/health/ready"
for i in $(seq 1 45); do
  if curl -sf "$ready_url" >/dev/null; then
    echo "GET /health/ready -> $(curl -sf "$ready_url")"
    break
  fi
  echo "  wait ready $i..."
  sleep 2
  if [[ "$i" -eq 45 ]]; then
    echo "backend not ready at $ready_url" >&2
    exit 1
  fi
done

py=""
if [[ -x "$ROOT/backend/.venv-acceptance/bin/python" ]]; then
  py="$ROOT/backend/.venv-acceptance/bin/python"
elif [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  py="$ROOT/backend/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  py="$(command -v python3)"
else
  py="$(command -v python)"
fi

if ! "$py" -c "import httpx, sqlalchemy" 2>/dev/null; then
  echo "Creating acceptance venv..."
  venv="$ROOT/backend/.venv-acceptance"
  python3 -m venv "$venv"
  py="$venv/bin/python"
  "$py" -m pip install -U pip
  "$py" -m pip install -e "$ROOT/backend[dev]"
fi

export DATABASE_URL="postgresql://patchhive:${DB_PASSWORD}@localhost:${DB_PORT}/patchhive"
export STAGING_API_URL="http://localhost:${API_PORT}"
export PYTHONPATH="$ROOT/backend"

echo "=== Walkthrough script ==="
"$py" "$ROOT/scripts/staging/design_engine_walkthrough.py"

echo "=== List design_packs in container ==="
compose exec -T backend sh -c 'ls -la /app/exports/design_packs 2>/dev/null | head -20' || true

echo ""
echo "DESIGN ENGINE STAGING WALKTHROUGH PASS"
echo "  UI: Style Studio on http://localhost:${FE_PORT} (flags on backend)"
echo "  Payments remain fail-closed."
