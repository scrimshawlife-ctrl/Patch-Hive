# Cases catalog — staging bootstrap (C3)

**Status:** operational  
**Related:** research fixture `fixtures/cases_research_2026.json`, `just cases-*`

## Goal

Ensure a staging or staging-like stack has the 50-case research catalog after migrations, without inventing power figures.

## Steps

```bash
# 1. Migrate (includes format_family / capacity_unit / powered)
cd backend && alembic upgrade head
# expect head: 20260721_case_format_columns

# 2. Validate fixture against CaseCreate
cd .. && just cases-dry-run

# 3. Import / replace ResearchCSV rows
export DATABASE_URL=postgresql://…   # staging DB
just cases-import --replace-source
```

Local staging compose:

```bash
export STAGING_DB_PASSWORD=…
export DATABASE_URL="postgresql://patchhive:${STAGING_DB_PASSWORD}@localhost:5432/patchhive"
just cases-import --replace-source
curl -s "http://localhost:8000/api/cases?format_family=Eurorack&limit=5" | head
```

## Semantics

| Column | Meaning |
|--------|---------|
| `format_family` | Eurorack / Buchla / 5U MU / Serge 4U / Frac |
| `capacity_unit` | `hp` or non-HP unit name |
| `powered` | product flag; independent of rail numbers |
| `power_*_ma` | null = unspecified (never invent); int = enforce on place |

Rack placement MVP: **Eurorack only**. Non-Eurorack rows remain catalog-only.

## Re-parse research markdown

```bash
just cases-parse   # fixtures/Cases4PatchHive.md → cases_research_2026.json
```
