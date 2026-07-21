# PatchHive roadmap

## Roadmap rules

This roadmap is capability- and evidence-based. Dates are not commitments unless separately approved. A phase advances only when its exit criteria are satisfied on an identified source SHA.

Status vocabulary:

- `COMPLETE` — merged and validated with retained evidence.
- `ACTIVE` — currently authorized work.
- `PLANNED` — sequenced but not started.
- `DEFERRED` — intentionally outside the current release line.
- `NOT_COMPUTABLE` — evidence is unavailable or insufficient.

## Retroactive release map

| Line | Maturity | Scope | Current classification |
|---|---|---|---|
| `0.1.x` | historical prototype | early rig, patch, publishing, and experimental surfaces | superseded or compatibility-only |
| `0.2.x` | canon-aligned MVP | immutable rigs/runs, deterministic compiler, validation, canonical export/credit boundary | implemented in part; not production released |
| `0.3.x` | Patch Book Generator | exactly one standalone page per patch, page-fit compiler, deterministic book manifests | specification complete; implementation planned |
| `0.4.x` | release hardening | catalog truth, operational maturity, accessibility and export conformance | planned |
| `1.0.0` | production-supported release | stable public workflow with supportable operations and no release blockers | not yet eligible |

## `0.2.x` — Canon-aligned MVP stabilization

**Objective:** establish one truthful runtime and eliminate high-risk dual paths.

### Required work

- complete migration of acceptance tests to canonical export and credit APIs;
- remove or fail-close legacy debit paths;
- expose server-authored rig revision and artifact manifest identities;
- quarantine historical UI and package surfaces;
- preserve deterministic compile, immutable runs, and append-only ledgers;
- validate staging PostgreSQL, migration, backup, and restore behavior;
- Visual System Intelligence P0 contracts: secure image evidence, provider-neutral adapters, confirmation → immutable inventory, confirmed-hardware patch gates (see `docs/VISUAL_SYSTEM_INTELLIGENCE_ROADMAP.md`).

### Exit criteria

- one canonical debit path;
- one authoritative run/export identity path;
- no enabled legacy social or publishing features;
- CI, integration, security, and accessibility gates pass;
- staging release receipt exists.

## `0.3.0-alpha` — Patch page contracts

**Objective:** make one-page publication constraints executable.

### Deliverables

- versioned `PatchPageSpec`, `PageFitReport`, and `PatchBookManifest` contracts;
- content budget and typography profile definitions;
- deterministic route numbering and cable classifications;
- page-fit error taxonomy;
- fixtures for simple, dense, feedback, and inaccessible patches.

### Exit criteria

- schema validation and compatibility tests pass;
- fixed inputs produce byte-equivalent canonical JSON;
- invalid overflow is rejected rather than clipped.

## `0.3.0-beta` — Rendering and book assembly

**Objective:** produce complete deterministic Patch Books.

### Deliverables

- semantic page assembler;
- SVG-first technical diagram renderer;
- diagram-first, instruction-first, and performance-first layouts;
- PDF, SVG, JSON, and ZIP export assembly;
- reading order, grayscale, and non-color encoding support;
- manifest binding and artifact checksums.

### Exit criteria

- every accepted patch compiles to exactly one page;
- page count equals accepted patch count plus declared front/back matter;
- golden, property, accessibility, and visual-regression suites pass;
- repeated builds from the same normalized inputs match declared determinism guarantees.

## `0.3.0-rc` — Patch Book release candidate

**Objective:** freeze the feature set and prove release behavior.

### Required evidence

- clean candidate SHA and release receipt;
- full supported-format export matrix;
- large-book and dense-patch performance tests;
- corrupted artifact, retry, reversal, and idempotency tests;
- tagged PDF checks where supported;
- manual print inspection for supported trim profiles;
- no unresolved P0/P1 defects;
- documented P2 defects with explicit acceptance.

## `0.4.x` — Production hardening

**Objective:** remove operational uncertainty before public production use.

### Workstreams

- module-gallery provenance and revision operations;
- admin correction and audit workflows;
- real upload scanning and provider isolation;
- SLOs, alerts, dead-letter handling, and reconciliation;
- backup restoration drills and disaster recovery;
- rate limiting, abuse controls, privacy retention, and support tooling;
- production payment readiness without activation by default;
- customer-facing help, methodology, and failure recovery.

## `1.0.0` — Production-supported release

PatchHive reaches `1.0.0` only when:

- canonical core workflows are stable and supportable;
- compatibility policy is enforced;
- migrations and backup recovery are proven;
- production security and privacy review has no unresolved critical/high findings;
- accessibility acceptance passes;
- deterministic export and manifest behavior is demonstrated;
- operational ownership and incident response exist;
- legal, billing, licensing, and support surfaces are approved;
- an explicit operator decision authorizes production deployment.

## Visual System Intelligence (cross-cutting)

Authoritative contracts: `docs/VISUAL_SYSTEM_INTELLIGENCE.md`, ADR-005, delivery plan in
`docs/VISUAL_SYSTEM_INTELLIGENCE_ROADMAP.md`.

| Priority | Capability | Status (evidence) |
|----------|------------|-------------------|
| P0 | Secure image re-encode + local quality | IMPLEMENTED (unit tests) |
| P0 | Provider-neutral vision adapter + mock/fixture | IMPLEMENTED (unit tests) |
| P0 | Classification candidates cannot self-confirm | IMPLEMENTED (contracts + runes) |
| P0 | Confirmation → immutable `SystemInventoryRevision` | IMPLEMENTED (in-process; ORM follow-on) |
| P0 | Confirmed-inventory patch constraint enforcement | IMPLEMENTED (unit tests) |
| P0 | Full HTTP confirmation + multi-photo UI workflow | PARTIAL (RackBuilder evidence UI; no multi-photo) |
| P1 | Port/control/cable reconstruction | STUB / mock empty |
| P1 | Photo-derived Patch Books | SPEC_ONLY |
| P2 | Live camera guidance, marketplace, community match | DEFERRED |

**Out of scope forever unless product canon changes:** audio recording, waveform analysis as ground truth, DSP engines, MIDI/CV hardware activation, DAW/plugin hosting.

## Deferred beyond 1.0

Unless separately authorized:

- community social graph;
- marketplace and public publishing network;
- leaderboards and contests;
- multiplayer or collaboration;
- hardware control, MIDI/CV activation, or DSP;
- automatic electrical-safety certification;
- arbitrary plugin execution;
- audio simulation presented as ground truth.
