# PatchHive production readiness

## Decision model

Production readiness is evaluated against evidence from an exact source SHA. It is not inferred from feature completion, CI success alone, a release-candidate label, or a successful local demonstration.

Readiness states:

- `PASS` — required evidence exists and satisfies the gate.
- `FAIL` — evidence demonstrates the gate is not satisfied.
- `NOT_COMPUTABLE` — required evidence is missing, stale, partial, or inaccessible.
- `WAIVED` — an authorized owner accepts a bounded non-critical risk with rationale and expiry.

Critical security, integrity, payment, data-loss, or accessibility blockers cannot be waived for a production-supported release.

## Current posture

**Classification:** development / pre-release.

The canon-aligned MVP and one-page Patch Book specifications do not establish production readiness. Production deployment, live payments, and customer charging remain unauthorized until the gates below pass and an explicit release decision is recorded.

## Release maturity ladder

### Development build

May contain partial flows and development fixtures. No compatibility or operational-support promise.

### Alpha

Core architecture and contracts exist, but scope and schemas may change. Intended for engineering evaluation.

### Beta

Declared feature scope is complete enough for controlled user validation. Known defects, incomplete operations, and compatibility changes remain possible.

### Release candidate

Feature and contract freeze for the declared release. Only release-blocking corrections are permitted. Every correction creates a new candidate.

### General availability

Production-supported release with proven operations, compatibility policy, incident response, support boundaries, and explicit authority.

## Readiness gates

### 1. Product and scope

- declared release scope is frozen;
- required user journeys complete without hidden legacy paths;
- excluded features are disabled and inaccessible;
- error, empty, loading, retry, stale, and degraded states are implemented;
- known issues are classified by severity and user impact.

### 2. Canonical integrity and determinism

- immutable rig, run, patch-library, patch, and export identities are enforced;
- canonical serialization and hash tests pass;
- fixed normalized inputs reproduce declared outputs;
- generator and renderer versions are embedded in artifacts;
- one-page invariant holds for every accepted published patch;
- overflow, missing technical truth, and unsupported capability claims fail closed.

### 3. Data and migrations

- exactly one migration head exists;
- clean install and upgrade from the oldest supported version pass;
- migration rollback/recovery strategy is tested;
- backup creation, encrypted retention, and restoration drills pass;
- referential integrity and append-only ledger invariants are verified;
- retention and deletion behavior is documented.

### 4. Security and privacy

- threat model is current;
- no unresolved critical or high findings;
- dependency, secret, static-analysis, and supply-chain scans pass;
- SBOM and build provenance are retained;
- uploads are type-checked, bounded, re-encoded, metadata-stripped, and scanned;
- provider output and image text are treated as untrusted data;
- authentication, authorization, tenant isolation, signed URLs, and admin re-authentication are tested;
- privacy policy, data inventory, retention, and incident handling are approved.

### 5. Billing and financial integrity

Required only for a release containing payments:

- production credentials are isolated from test credentials;
- webhook signatures, replay handling, and idempotency pass;
- debit, reversal, refund, and reconciliation paths are tested under concurrency;
- no duplicate charge or export occurs under retry;
- ledger imbalance alerting and operational runbooks exist;
- live activation requires a separate explicit authority decision.

### 6. Accessibility and publication quality

- WCAG 2.2 AA acceptance is complete for core flows;
- keyboard-only and screen-reader protocols pass;
- graph content has an equivalent ordered representation;
- no color-only status, signal, or cable meaning exists;
- supported PDFs have verified reading order and tagging where available;
- print profiles meet typography, margin, bleed, grayscale, and QR constraints;
- manual inspection covers representative simple, dense, feedback, and warning-heavy pages.

### 7. Reliability and performance

- API and worker load tests cover expected and burst traffic;
- queue delay, compile duration, export duration, and storage failure budgets are defined;
- bounded retry, dead-letter, cancellation, and terminal-failure behavior is tested;
- large Patch Books stay within memory, time, and file-size budgets;
- database connection, object-storage, and provider outages degrade safely;
- SLOs and alert thresholds are approved.

### 8. Observability and operations

- structured logs, metrics, traces, and error reporting include correlation IDs;
- dashboards cover API, jobs, exports, ledger, storage, and provider health;
- on-call or named operational ownership exists;
- incident, rollback, reconciliation, artifact withdrawal, and disaster-recovery runbooks are tested;
- release and deployment receipts are retained;
- staging matches production topology closely enough to validate critical paths.

### 9. Compatibility and release engineering

- versioning policy is followed;
- API, contract, artifact, generator, and renderer versions are declared;
- changelog and migration notes are complete;
- candidate tag points to the tested SHA;
- dependency locks and container/build identities are immutable;
- installation, upgrade, rollback, and artifact-reader compatibility are validated;
- release artifacts include checksums, SBOM, provenance, and signatures when supported.

### 10. Legal, support, and governance

- license and third-party notices are correct;
- export license terms and customer-facing claims are approved;
- support channel, response expectations, and escalation owner exist;
- safety language distinguishes documentation from electrical certification;
- operator authority explicitly approves deployment and any live payment activation.

## Release candidate checklist

A candidate is eligible only when all entries are recorded against one SHA:

```yaml
release_candidate:
  version:
  source_sha:
  migration_head:
  contract_versions: {}
  generator_version:
  renderer_version:
  release_scope_frozen: false
  automated_tests: NOT_COMPUTABLE
  postgres_integration: NOT_COMPUTABLE
  migration_upgrade: NOT_COMPUTABLE
  backup_restore: NOT_COMPUTABLE
  deterministic_replay: NOT_COMPUTABLE
  page_fit_matrix: NOT_COMPUTABLE
  accessibility: NOT_COMPUTABLE
  security: NOT_COMPUTABLE
  sbom_provenance: NOT_COMPUTABLE
  load_reliability: NOT_COMPUTABLE
  billing_integrity: NOT_APPLICABLE
  staging_acceptance: NOT_COMPUTABLE
  known_blockers: []
  waivers: []
  authority_decision: NOT_GRANTED
```

## Severity and release policy

- **P0 / Critical:** data loss, cross-user access, arbitrary execution, payment duplication, irreversible ledger corruption, unsafe secret exposure. Blocks every candidate and release.
- **P1 / High:** broken core journey, deterministic integrity failure, inaccessible core workflow, unrecoverable export failure, migration failure. Blocks RC and GA.
- **P2 / Medium:** bounded defect with workaround and no integrity loss. May enter RC only when documented and explicitly accepted.
- **P3 / Low:** cosmetic or minor usability issue. Does not normally block RC.

## Final authority

Passing technical gates makes a build eligible for release; it does not deploy it. Production deployment and live payment activation require a separate, explicit operator decision naming the version, SHA, environment, and approved capabilities.
