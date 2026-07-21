# Visual System Intelligence Delivery Roadmap

**Status:** Implementation plan  
**Authority:** Subordinate to `CURRENT_STATE.md`, explicit canon, and release governance

## Outcome

Deliver a trustworthy path from user system photographs to a confirmed canonical inventory, hardware-constrained patch suggestions, and deterministic Patch Books.

## Workstream 0 — Baseline and contract alignment

### Deliverables

- pin exact baseline SHA and toolchain
- inventory all existing photo/manual/hybrid ingestion code and schemas
- map active, transitional, legacy, and missing surfaces
- align repository docs and Notion canon
- add contract tests preventing vision output from directly mutating canonical rig state

### Exit criteria

- one documented authority chain
- no duplicate canonical system models
- all unresolved contradictions recorded as explicit gaps

## Workstream 1 — Secure image evidence intake

### Deliverables

- authenticated upload endpoint
- MIME sniffing and image re-encoding
- size, dimension, decompression-bomb, and malware controls
- metadata stripping and retention policy
- content hash and evidence record
- image-quality assessment for blur, glare, coverage, rotation, and perspective

### Exit criteria

- hostile-file tests pass
- every accepted image has immutable evidence identity
- rejected images return machine-readable reasons

## Workstream 2 — Device Registry readiness

### Deliverables

- canonical manufacturer, device, module, revision, alias, panel-image, port, control, and capability schemas
- registry provenance and revision history
- exact and fuzzy retrieval surfaces
- unknown-class support
- catalog completeness metrics

### Exit criteria

- registry records are versioned and auditable
- candidate retrieval is reproducible for fixed registry version and query packet
- missing specifications remain missing

## Workstream 3 — P0 module/device recognition

### Deliverables

- rack/device/module region detection
- logo, OCR, panel, geometry, and embedding evidence extraction
- ranked Device Registry candidates
- confidence calibration
- candidate alternatives and evidence display
- recognition receipts containing provider/model/version identity

### Exit criteria

- evaluation dataset and license/provenance manifest retained
- top-1/top-k and unknown-rejection thresholds defined and met
- no provider result is treated as canonical without confirmation-policy evaluation

## Workstream 4 — Confirmation and canonical inventory

### Deliverables

- confirm, reject, replace, defer, and manual-add actions
- duplicate resolution
- position correction
- unresolved-item workflow
- immutable `SystemInventoryRevision`
- deterministic `SystemCapabilityGraph`

### Exit criteria

- user-confirmed facts supersede inference while preserving evidence
- inventory revisions are immutable
- patch generation cannot start against unresolved release-blocking data

## Workstream 5 — System-constrained patch suggestions

### Deliverables

- patch request schema for goal, mood, genre, complexity, performance context, and constraints
- capability-aware module and port selection
- ordered connection plan
- initial controls, modes, prerequisites, listening cues, variations, and troubleshooting
- validation against confirmed device capabilities
- substitution and degradation reporting

### Exit criteria

- no generated patch silently requires unavailable hardware
- every connection resolves to confirmed ports or is rejected
- validation receipts bind patch, rig revision, registry version, generator version, and seed

## Workstream 6 — Multi-photo reconciliation

### Deliverables

- cross-image entity association
- alternate-angle reconciliation
- duplicate and occlusion handling
- coverage guidance and missing-view requests
- fused evidence packet with per-claim provenance

### Exit criteria

- reconciliation accuracy measured independently from single-image recognition
- conflicting evidence remains explicit and reviewable

## Workstream 7 — Rack, control, port, and cable reconstruction

### Deliverables

- physical rack/workspace layout
- control and port candidate detection
- cable segment tracing
- probable endpoint association
- crossing and occlusion ambiguity handling
- editable inferred connection graph
- feedback-loop and signal-domain checks

### Exit criteria

- obscured endpoints are never marked `OBSERVED`
- endpoint and graph accuracy meet defined P1 thresholds
- users can correct every inferred connection

## Workstream 8 — Photo-derived Patch Books

### Deliverables

- confirmed system overview
- inventory and module glossary
- rack layout
- system-specific patch recipes
- cable diagrams and ordered connection tables
- settings, listening cues, variations, warnings, and troubleshooting
- confidence and unresolved-data annotations
- source-image, rig-revision, run, generator, and manifest lineage

### Exit criteria

- one-patch-per-page invariant passes
- diagram and ordered cable table encode the same graph
- deterministic replay produces stable canonical JSON and SVG structure
- PDF/SVG/JSON/ZIP manifests resolve all references

## Workstream 9 — Production hardening

### Deliverables

- privacy and deletion verification
- rate limits and abuse controls
- provider outage and fallback behavior
- observability and cost telemetry
- dataset and model drift monitoring
- backup/restore and migration tests
- accessibility validation for confirmation and graph workflows
- support runbooks

### Exit criteria

- production-readiness matrix completed on an exact SHA
- no `NOT_COMPUTABLE` release blocker remains
- explicit release authority approves activation

## Required metrics

- image acceptance and quality-failure rates
- module detection precision/recall
- manufacturer and exact-model top-1/top-k accuracy
- unknown-class rejection quality
- confidence calibration error
- multi-photo reconciliation accuracy
- control and port detection accuracy
- cable endpoint and graph accuracy
- user correction rate
- median time to confirmed inventory
- patch validation pass rate
- unavailable-hardware violation rate
- Patch Book compile and page-fit success rates

## Delivery rule

Each workstream must ship through a bounded branch and pull request with:

- baseline SHA
- contracts changed
- migrations and compatibility impact
- tests and evaluation receipts
- security/privacy review
- documentation updates
- unresolved risks labeled `NOT_COMPUTABLE`
