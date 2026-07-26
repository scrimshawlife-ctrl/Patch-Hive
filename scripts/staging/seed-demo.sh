#!/usr/bin/env bash
# Seed golden demo users + rig into local staging Compose Postgres.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DB_PORT="${STAGING_DB_PORT:-5433}"
DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"

if [[ -x "$ROOT/backend/.venv-acceptance/bin/python" ]]; then
  py="$ROOT/backend/.venv-acceptance/bin/python"
elif [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  py="$ROOT/backend/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  py="$(command -v python3)"
else
  py="$(command -v python)"
fi

if ! "$py" -c "import sqlalchemy" 2>/dev/null; then
  echo "Installing backend[dev] into .venv-acceptance..."
  python3 -m venv "$ROOT/backend/.venv-acceptance"
  py="$ROOT/backend/.venv-acceptance/bin/python"
  "$py" -m pip install -U pip
  "$py" -m pip install -e "$ROOT/backend[dev]"
fi

export DATABASE_URL="postgresql://patchhive:${DB_PASSWORD}@localhost:${DB_PORT}/patchhive"
export PYTHONPATH="$ROOT/backend"
export TEST_MODE=true
export STRIPE_TEST_MODE=true
export ALLOW_PRODUCTION_PAYMENTS=false

echo "=== Seed golden demo (localhost:${DB_PORT}) ==="
"$py" "$ROOT/scripts/seed_golden_demo.py"
echo "DEMO SEED PASS"
echo "  User:  golden_demo / demo-pass"
echo "  Admin: admin / admin-pass"
