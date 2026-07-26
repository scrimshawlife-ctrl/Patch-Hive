#!/usr/bin/env bash
# Full local Docker staging suite (Linux/macOS).
# See scripts/staging/docker-suite.ps1 for Windows.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export STAGING_API_PORT="${STAGING_API_PORT:-18000}"
export STAGING_FE_PORT="${STAGING_FE_PORT:-15173}"
export STAGING_DB_PORT="${STAGING_DB_PORT:-5433}"
export STAGING_PUBLIC_API_URL="${STAGING_PUBLIC_API_URL:-http://localhost:${STAGING_API_PORT}}"
export STAGING_CORS_ORIGINS="${STAGING_CORS_ORIGINS:-http://localhost:${STAGING_FE_PORT},http://localhost:5173}"
export STAGING_SECRET_KEY="${STAGING_SECRET_KEY:-staging-smoke-secret-key-min-32-chars-xx}"
export STAGING_DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"
SKIP_BUILD="${SKIP_BUILD:-0}"
SKIP_ACCEPTANCE="${SKIP_ACCEPTANCE:-0}"
SKIP_DESIGN_ENGINE="${SKIP_DESIGN_ENGINE:-0}"

echo "========================================"
echo " Docker staging suite"
echo " API :${STAGING_API_PORT}  FE :${STAGING_FE_PORT}  DB :${STAGING_DB_PORT}"
echo "========================================"

echo ""
echo "--- [1/3] smoke ---"
if [[ "$SKIP_BUILD" == "1" ]]; then
  SKIP_BUILD=1 bash scripts/staging/smoke.sh
else
  bash scripts/staging/smoke.sh
fi

if [[ "$SKIP_ACCEPTANCE" != "1" ]]; then
  echo ""
  echo "--- [2/3] acceptance (docker network) ---"
  bash scripts/staging/acceptance-docker.sh
else
  echo ""
  echo "--- [2/3] acceptance SKIPPED ---"
fi

if [[ "$SKIP_DESIGN_ENGINE" != "1" ]]; then
  echo ""
  echo "--- [3/3] design-engine ---"
  if [[ "$SKIP_BUILD" == "1" ]]; then
    SKIP_BUILD=1 bash scripts/staging/design-engine.sh
  else
    bash scripts/staging/design-engine.sh
  fi
else
  echo ""
  echo "--- [3/3] design-engine SKIPPED ---"
fi

echo ""
echo "DOCKER STAGING SUITE PASS"
echo "  API:  http://localhost:${STAGING_API_PORT}/health/ready"
echo "  FE:   http://localhost:${STAGING_FE_PORT}"
echo "  Payments fail-closed."
