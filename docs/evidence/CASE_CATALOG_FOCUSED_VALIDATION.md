# Case catalog focused validation (2026-07-21)

Artifacts from `case-catalog-focused-validation-4.zip` (fail) and
`case-catalog-focused-validation-pass.zip` (pass).

## Fail (`validation-4`)

CLI dry-run crashed during mapper configuration:

```text
sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[User(users)],
expression 'CreditLedgerEntry' failed to locate a name ('CreditLedgerEntry').
```

Stack: `case_catalog_populator.import_records` → `db.query(CaseCatalog)`.

**Cause:** Integration CLI used `SessionLocal` without importing the full model graph.

**Fix:** `backend/integrations/__init__.py` registers the same relationship graph as `tests/conftest.py` (includes `account.models.CreditLedgerEntry`).

## Pass (`validation-pass`)

Dry-run receipt (example, `schema.example.json`):

```json
{
  "dry_run": true,
  "input_path": "../data/cases/schema.example.json",
  "input_records": 1,
  "input_sha256": "f8c27c506e55885c7dc56a2f0c011105c36b99c9c39fe63f17eb7a68d7cafa96",
  "inserted": 1,
  "rejected": 0,
  "status": "success",
  "updated": 0,
  "warnings": []
}
```

Also saved as `CASE_CATALOG_DRY_RUN_PASS_RECEIPT.json`.
