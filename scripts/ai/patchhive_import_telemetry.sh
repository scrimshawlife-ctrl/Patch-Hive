#!/usr/bin/env bash
# Print a live snapshot of patchhive package import density (stdout).
# Does not rewrite the markdown doc automatically (human/agent merges into telemetry file).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "# patchhive import telemetry snapshot"
echo "cwd: $ROOT"
echo "date: $(date -u +%Y-%m-%dT%H:%MZ)"
if git rev-parse --short HEAD >/dev/null 2>&1; then
  echo "git_head: $(git rev-parse --short HEAD)"
fi
echo

echo "## canon/evidence → patchhive package"
if rg -n --glob '*.py' -e '(from[[:space:]]+patchhive|import[[:space:]]+patchhive)' backend/canon backend/evidence 2>/dev/null; then
  echo "(hits above — FAIL if package imports)"
else
  echo "NONE (OK)"
fi
echo

echo "## backend/tests files importing patchhive"
rg -l --glob '*.py' -e '(from[[:space:]]+patchhive|import[[:space:]]+patchhive)' backend/tests 2>/dev/null | sort || true
echo

echo "## heaviest backend importers (top 20)"
rg -c --glob '*.py' -e '(from[[:space:]]+patchhive|import[[:space:]]+patchhive)' backend 2>/dev/null \
  | sort -t: -k2 -nr | head -20 || true
echo

echo "## tree sizes (py files)"
echo -n "backend/patchhive: "; find backend/patchhive -name '*.py' 2>/dev/null | wc -l | tr -d ' '
echo -n "repo-root patchhive/: "; find patchhive -name '*.py' 2>/dev/null | wc -l | tr -d ' '
echo

echo "## guard"
bash scripts/ai/check_no_canon_patchhive_imports.sh
