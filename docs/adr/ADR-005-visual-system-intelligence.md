# ADR-005: Visual System Intelligence Extends Rig Ingestion

- **Status:** Accepted
- **Date:** 2026-07-20
- **Decision type:** Product architecture and trust boundary

## Context

PatchHive already supports manual, photo-assisted, and hybrid rig ingestion. Existing descriptions did not fully specify multi-photo system analysis, exact module/device classification, visible cable inference, system-capability modeling, or photo-derived Patch Book generation.

Treating those capabilities as a separate subsystem would duplicate the Device Registry, evidence, confirmation, rig revision, patch generation, and publishing contracts.

## Decision

Visual System Intelligence is an extension of the canonical ingestion and resolution bounded context.

The authoritative flow is:

```text
Image evidence
  -> candidate detection and classification
  -> Device Registry retrieval
  -> confirmation-policy evaluation
  -> immutable system inventory revision
  -> deterministic capability graph
  -> deterministic patch generation
  -> deterministic Patch Book compilation
```

Nondeterministic provider output is evidence only and cannot directly mutate canonical rig state.

All detected or inferred entities must carry evidence, provenance, confidence, provider/model identity, candidate alternatives, confirmation state, and schema/registry versions.

## Consequences

### Positive

- Preserves one canonical rig and patch model.
- Prevents provider-specific vision output from becoming authority.
- Enables patches that are valid for the user's confirmed hardware.
- Supports incremental capability from module recognition through cable reconstruction.
- Retains reproducibility and auditability for Patch Books.

### Costs

- Requires a versioned Device Registry and representative evaluation dataset.
- Requires human confirmation UX and immutable inventory revisions.
- Requires confidence calibration and unknown-class rejection.
- Cable reconstruction remains ambiguous in many real-world images and must fail open to user review, not false certainty.

## Priority

- **P0:** image intake, quality assessment, module/device candidates, confirmation, canonical inventory, system-constrained patch suggestions.
- **P1:** multi-photo reconciliation, layout reconstruction, port/control detection, cable endpoint inference, photo-derived Patch Books.
- **P2:** guided live capture, advanced layout optimization, opt-in commercial recommendations, community system similarity.

## Related documents

- `docs/VISUAL_SYSTEM_INTELLIGENCE.md`
- `docs/VISUAL_SYSTEM_INTELLIGENCE_ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/PATCH_ENGINE.md`
- `docs/PATCH_BOOK_GENERATOR.md`
- `docs/PRODUCTION_READINESS.md`
