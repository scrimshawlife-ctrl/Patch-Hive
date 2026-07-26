#!/usr/bin/env bash
# Run backend acceptance suite entirely inside Docker (compose network).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export STAGING_DB_PASSWORD="${STAGING_DB_PASSWORD:-staging-smoke-db-pass-xx}"
export STAGING_DB_PORT="${STAGING_DB_PORT:-5433}"
export STAGING_API_PORT="${STAGING_API_PORT:-18000}"
export STAGING_FE_PORT="${STAGING_FE_PORT:-15173}"
export STAGING_SECRET_KEY="${STAGING_SECRET_KEY:-staging-smoke-secret-key-min-32-chars-xx}"
export STAGING_PUBLIC_API_URL="${STAGING_PUBLIC_API_URL:-http://localhost:${STAGING_API_PORT}}"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.staging.yml}"
ACCEPTANCE_COMPOSE="${ACCEPTANCE_COMPOSE:-docker-compose.staging.acceptance.yml}"

mkdir -p tmp/acceptance-docker

echo "=== Ensure staging db is up ==="
docker compose -f "$COMPOSE_FILE" up -d db

echo "=== Docker acceptance (in-network pytest) ==="
docker compose -f "$COMPOSE_FILE" -f "$ACCEPTANCE_COMPOSE" run --rm --no-deps acceptance

echo "DOCKER ACCEPTANCE PASS"
