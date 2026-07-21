# Release checklist

## Pre-release

- [ ] `alembic heads` shows exactly one head
- [ ] CI green on exact SHA (Backend Tests, Code Quality, Security)
- [ ] `CURRENT_STATE.md` HEAD matches tag candidate
- [ ] Changelog entry for user-visible changes
- [ ] Feature flags: legacy social/publish off; `ALLOW_PRODUCTION_PAYMENTS=false`
- [ ] No secrets in tree (`gitleaks` clean)
- [ ] Migration upgrade path documented

## Product scope

- [ ] No audio-processing product claims
- [ ] Vision self-confirm still rejected by tests
- [ ] Production readiness matrix not claiming PASS without evidence

## Deploy authority

- [ ] Explicit operator decision for environment
- [ ] Staging drill preferred before public traffic
- [ ] Payments activation is a **separate** decision

## Post-release

- [ ] Tag + release notes
- [ ] Update `CURRENT_STATE.md`
- [ ] Invalidate/rebuild `.codebase-memory` indexes on major moves

See also: `docs/PRODUCTION_READINESS.md`, `docs/OPERATIONS.md`, `docs/VERSIONING.md`.
