#!/bin/bash
set -euo pipefail

echo "Starting PatchHive Backend..."

# Wait for PostgreSQL when DATABASE_URL points at a network host (best-effort).
if [ -n "${DATABASE_URL:-}" ] && command -v pg_isready >/dev/null 2>&1; then
    echo "Waiting for PostgreSQL (if configured)..."
    # Best-effort: many hosts set DATABASE_HOST; otherwise skip tight wait.
    if [ -n "${DATABASE_HOST:-}" ]; then
        until pg_isready -h "${DATABASE_HOST}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-patchhive}" 2>/dev/null; do
            echo "PostgreSQL is unavailable - sleeping"
            sleep 2
        done
        echo "PostgreSQL is up!"
    fi
fi

# Schema must come from Alembic, not create_all().
# Default: run migrations when RUN_MIGRATIONS is unset or true (staging/prod compose).
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
if [ "$RUN_MIGRATIONS" = "true" ] || [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running database migrations (alembic upgrade head)..."
    python -m alembic upgrade head
    echo "Migrations applied."
fi

exec "$@"
