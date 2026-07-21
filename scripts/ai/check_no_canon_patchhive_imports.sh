#!/usr/bin/env bash
# Fail if product CANON_MVP packages import the historical patchhive package.
# Schema version strings containing "patchhive." are allowed (not import statements).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TARGETS=(backend/canon backend/evidence)
PATTERN='(^|[[:space:]])(from[[:space:]]+patchhive(\\.|[[:space:]])|import[[:space:]]+patchhive)([[:space:]]|,|$)'

hits="$(rg -n --glob '*.py' -e "$PATTERN" "${TARGETS[@]}" 2>/dev/null || true)"
if [[ -n "${hits}" ]]; then
  echo "ERROR: forbidden import of historical package 'patchhive' from CANON_MVP paths:" >&2
  echo "${hits}" >&2
  echo "Implement on canon/evidence instead. See docs/engineering/PATCHHIVE_IMPORT_TELEMETRY.md" >&2
  exit 1
fi

echo "OK: no package-level patchhive imports under ${TARGETS[*]}"
