# Operations and deployment

PatchHive remains a modular monolith. Apply the single Alembic head before application rollout, then start the FastAPI and static frontend processes. Production persistence is PostgreSQL; SQLite is a unit-test adapter only.

## Release gates

1. Install exactly from `backend/pyproject.toml` and `frontend/package-lock.json`.
2. Run backend, frontend, property/contract, security, and accessibility automation.
3. Run `alembic heads` and require exactly `20240927_canon_alignment`.
4. Run PostgreSQL integration and migration tests.
5. Generate and retain Python/npm CycloneDX SBOMs and build provenance.
6. Run `reconcile_ledger` and require no anomalies.
7. Verify all legacy feature flags are false.
8. Verify Stripe test mode is true and production payments are false.
9. Perform the manual accessibility protocol.

## Failure recovery

- A terminal export failure creates one immutable reversal keyed to the export and changes the mutable export state to refunded.
- Repeated export requests return the existing idempotent export and do not debit again.
- Replayed Stripe events with identical payloads are no-ops; a payload mismatch for the same event ID is rejected.
- Generation never overwrites a prior run; retry orchestration must create or resume an explicit job and preserve receipts.

No deployment or production payment activation was performed during the canon-alignment campaign.
