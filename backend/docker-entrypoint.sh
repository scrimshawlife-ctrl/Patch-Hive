#!/bin/bash
set -euo pipefail

echo "Starting PatchHive Backend..."

# Wait until DATABASE_URL accepts connections (Postgres recovery / compose race).
# Uses Python+psycopg2 so we do not depend on pg_isready or DATABASE_HOST.
wait_for_database() {
    if [ -z "${DATABASE_URL:-}" ]; then
        echo "DATABASE_URL unset — skipping DB wait"
        return 0
    fi
    # SQLite / empty: no wait
    case "${DATABASE_URL}" in
        sqlite:*|"" ) return 0 ;;
    esac

    local max_attempts="${DB_WAIT_ATTEMPTS:-60}"
    local sleep_secs="${DB_WAIT_INTERVAL:-2}"
    echo "Waiting for database (up to $((max_attempts * sleep_secs))s)..."
    local attempt=1
    while [ "$attempt" -le "$max_attempts" ]; do
        if python - <<'PY'
import os
import sys

url = os.environ.get("DATABASE_URL", "")
if not url or url.startswith("sqlite"):
    sys.exit(0)
try:
    import psycopg2
    # SQLAlchemy-style postgresql:// works with psycopg2 if we normalize scheme
    dsn = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    conn = psycopg2.connect(dsn, connect_timeout=3)
    conn.close()
    sys.exit(0)
except Exception as exc:
    print(f"  not ready: {type(exc).__name__}: {exc}", flush=True)
    sys.exit(1)
PY
        then
            echo "Database is accepting connections."
            return 0
        fi
        echo "  attempt ${attempt}/${max_attempts} — sleeping ${sleep_secs}s"
        sleep "$sleep_secs"
        attempt=$((attempt + 1))
    done
    echo "ERROR: database not ready after ${max_attempts} attempts" >&2
    return 1
}

wait_for_database

# Schema must come from Alembic, not create_all().
# Default: run migrations when RUN_MIGRATIONS is unset or true (staging/prod compose).
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
if [ "$RUN_MIGRATIONS" = "true" ] || [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running database migrations (alembic upgrade head)..."
    # Retry transient Postgres startup races even after wait (e.g. brief exclusive lock).
    migrate_attempts="${ALEMBIC_ATTEMPTS:-5}"
    migrate_ok=0
    for i in $(seq 1 "$migrate_attempts"); do
        if python -m alembic upgrade head; then
            migrate_ok=1
            break
        fi
        echo "alembic upgrade failed (attempt ${i}/${migrate_attempts}); retrying in 3s..."
        sleep 3
    done
    if [ "$migrate_ok" -ne 1 ]; then
        echo "ERROR: alembic upgrade head failed after ${migrate_attempts} attempts" >&2
        exit 1
    fi
    echo "Migrations applied."
fi

exec "$@"
