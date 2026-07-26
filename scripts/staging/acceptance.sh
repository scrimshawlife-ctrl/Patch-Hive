#!/usr/bin/env bash
# Run backend acceptance suite against local staging Compose Postgres.
# Uses dedicated DB patchhive_acceptance so the live staging API DB is not truncated.
#
# Prerequisites: Docker staging stack up (scripts/staging/smoke.sh or compose up).
#
# Usage (repo root):
#   bash scripts/staging/acceptance.sh
#   STAGING_DB_PORT=5433 bash scripts/staging/acceptance.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DB_PORT="${STAGING_DB_PORT:-5433}"
DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.staging.yml}"
ACCEPTANCE_DB="${ACCEPTANCE_DB:-patchhive_acceptance}"

export STAGING_DB_PORT="$DB_PORT"
export STAGING_DB_PASSWORD="$DB_PASSWORD"

compose() { docker compose -f "$COMPOSE_FILE" "$@"; }

if ! docker version >/dev/null 2>&1; then
  echo "Docker engine not available" >&2
  exit 1
fi

if ! compose ps --status running --services 2>/dev/null | grep -q '^db$'; then
  echo "Starting staging db..."
  compose up -d db
  sleep 5
fi

# Fresh DB each run so alembic upgrade head is deterministic (no half-migrated residue).
echo "=== Recreate acceptance database '${ACCEPTANCE_DB}' ==="
compose exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${ACCEPTANCE_DB}' AND pid <> pg_backend_pid();" \
  >/dev/null || true
compose exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${ACCEPTANCE_DB};"
compose exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${ACCEPTANCE_DB};"
echo "Created clean ${ACCEPTANCE_DB}"

accept_url="postgresql://patchhive:${DB_PASSWORD}@localhost:${DB_PORT}/${ACCEPTANCE_DB}"
echo "ACCEPTANCE_DATABASE_URL=${accept_url}"

py=""
if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  py="$ROOT/backend/.venv/bin/python"
elif [[ -x "$ROOT/backend/.venv-acceptance/bin/python" ]]; then
  py="$ROOT/backend/.venv-acceptance/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  py="$(command -v python3)"
else
  py="$(command -v python)"
fi

if ! "$py" -c "import pytest" 2>/dev/null; then
  echo "Creating venv + installing backend[dev]..."
  venv="$ROOT/backend/.venv-acceptance"
  python3 -m venv "$venv"
  py="$venv/bin/python"
  "$py" -m pip install -U pip
  "$py" -m pip install -e "$ROOT/backend[dev]"
fi

export ACCEPTANCE_DATABASE_URL="$accept_url"
export TEST_MODE=true
export STRIPE_TEST_MODE=true
export ALLOW_PRODUCTION_PAYMENTS=false
mkdir -p "$ROOT/tmp/acceptance-run/exports" "$ROOT/tmp/acceptance-run/pytest-tmp"
export ACCEPTANCE_EXPORT_DIR="$ROOT/tmp/acceptance-run/exports"
export TMPDIR="$ROOT/tmp/acceptance-run/pytest-tmp"

echo "=== pytest tests/acceptance ==="
(
  cd "$ROOT/backend"
  env -u PYTHONPATH "$py" -m pytest tests/acceptance -q --tb=short
)

echo "STAGING ACCEPTANCE PASS"
