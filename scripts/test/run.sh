#!/usr/bin/env bash
# PatchHive unified test runner (Linux/macOS/CI)
#
# Usage (repo root):
#   bash scripts/test/run.sh unit
#   bash scripts/test/run.sh acceptance
#   bash scripts/test/run.sh frontend
#   bash scripts/test/run.sh e2e
#   bash scripts/test/run.sh ci          # unit + frontend + acceptance (CI parity)
#   bash scripts/test/run.sh smoke       # local compose staging smoke
#   bash scripts/test/run.sh design-engine
#   bash scripts/test/run.sh staging     # smoke + compose acceptance + design-engine
#   bash scripts/test/run.sh docker-suite  # smoke + in-docker acceptance + design-engine
#   bash scripts/test/run.sh all         # unit + frontend + acceptance + e2e
#
# Env:
#   ACCEPTANCE_DATABASE_URL  skip Testcontainers when set
#   SKIP_BUILD=1             smoke/design-engine skip image rebuild
#   STRIPE_TEST_MODE=true    defaulted fail-closed payments

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SUITE="${1:-}"
if [[ -z "$SUITE" || "$SUITE" == "-h" || "$SUITE" == "--help" ]]; then
  sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
fi

export TEST_MODE="${TEST_MODE:-true}"
export STRIPE_TEST_MODE="${STRIPE_TEST_MODE:-true}"
export ALLOW_PRODUCTION_PAYMENTS="${ALLOW_PRODUCTION_PAYMENTS:-false}"

_backend_python() {
  if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
    echo "$ROOT/backend/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  else
    command -v python
  fi
}

_ensure_backend_dev() {
  local py
  py="$(_backend_python)"
  if ! "$py" -c "import pytest" 2>/dev/null; then
    echo "Installing backend[dev]..."
    (cd "$ROOT/backend" && "$py" -m pip install -e '.[dev]')
  fi
}

run_unit() {
  echo "=== suite: unit (backend, ignore acceptance) ==="
  _ensure_backend_dev
  local py
  py="$(_backend_python)"
  (
    cd "$ROOT/backend"
    env -u PYTHONPATH "$py" -m pytest tests --ignore=tests/acceptance -q --tb=short
  )
}

run_acceptance() {
  echo "=== suite: acceptance (backend) ==="
  _ensure_backend_dev
  local py
  py="$(_backend_python)"
  mkdir -p "$ROOT/tmp/acceptance-run/exports" "$ROOT/tmp/acceptance-run/pytest-tmp"
  export ACCEPTANCE_EXPORT_DIR="${ACCEPTANCE_EXPORT_DIR:-$ROOT/tmp/acceptance-run/exports}"
  export TMPDIR="${TMPDIR:-$ROOT/tmp/acceptance-run/pytest-tmp}"
  (
    cd "$ROOT/backend"
    env -u PYTHONPATH \
      TEST_MODE=true \
      STRIPE_TEST_MODE=true \
      ALLOW_PRODUCTION_PAYMENTS=false \
      "$py" -m pytest tests/acceptance -q --tb=short
  )
}

run_frontend() {
  echo "=== suite: frontend (vitest) ==="
  (
    cd "$ROOT/frontend"
    if [[ ! -d node_modules ]]; then
      npm ci
    fi
    npm test -- --run
  )
}

run_e2e() {
  echo "=== suite: e2e (playwright) ==="
  (
    cd "$ROOT/frontend"
    if [[ ! -d node_modules ]]; then
      npm ci
    fi
    npx playwright install --with-deps chromium 2>/dev/null || npx playwright install chromium
    npm run test:e2e
  )
}

run_smoke() {
  echo "=== suite: staging smoke ==="
  bash "$ROOT/scripts/staging/smoke.sh"
}

run_design_engine() {
  echo "=== suite: design-engine walkthrough ==="
  if [[ -f "$ROOT/scripts/staging/design-engine.sh" ]]; then
    bash "$ROOT/scripts/staging/design-engine.sh"
  else
    echo "design-engine.sh missing; use scripts/staging/design-engine.ps1 on Windows" >&2
    exit 1
  fi
}

run_staging_acceptance() {
  echo "=== suite: staging acceptance (compose Postgres) ==="
  bash "$ROOT/scripts/staging/acceptance.sh"
}

run_docker_suite() {
  echo "=== suite: docker-suite ==="
  bash "$ROOT/scripts/staging/docker-suite.sh"
}

case "$SUITE" in
  unit)
    run_unit
    ;;
  acceptance)
    run_acceptance
    ;;
  frontend)
    run_frontend
    ;;
  e2e)
    run_e2e
    ;;
  ci)
    run_unit
    run_frontend
    run_acceptance
    ;;
  smoke)
    run_smoke
    ;;
  design-engine)
    run_design_engine
    ;;
  staging)
    run_smoke
    run_staging_acceptance
    run_design_engine
    ;;
  docker-suite)
    run_docker_suite
    ;;
  all)
    run_unit
    run_frontend
    run_acceptance
    run_e2e
    ;;
  *)
    echo "Unknown suite: $SUITE" >&2
    echo "Use: unit|acceptance|frontend|e2e|ci|smoke|design-engine|staging|docker-suite|all" >&2
    exit 2
    ;;
esac

echo "TEST SUITE PASS: $SUITE"
