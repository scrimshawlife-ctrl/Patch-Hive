# Changelog

All notable changes to PatchHive are documented here.

This project follows [Semantic Versioning](docs/VERSIONING.md) beginning with the adoption of the formal release policy. Historical entries are reconstructed from repository evidence and are labeled as retroactive classifications rather than invented release tags.

## Unreleased

### Added

- Canonical one-page Patch Book publishing invariant.
- Comprehensive Patch Book Generator specification.
- Versioning and release-candidate policy.
- Evidence-based production-readiness framework.
- Versioned product roadmap.
- Visual System Intelligence P0 contracts: provider-neutral `VisionEvidenceProvider`, `SystemInventoryRevision`, `SystemCapabilityGraph`, confirmed-inventory patch constraint gate.
- Local image quality assessment after secure re-encode.
- Audit receipts under `docs/evidence/` (baseline, audio-drift classification, capability matrix, readiness matrix, work packages).

### Changed

- Root README rebuilt as the canonical repository entrypoint.
- Canon and operations documentation aligned to page-fit, deterministic export, and manifest requirements.
- `docs/PATCH_ENGINE.md`: audio simulation and hardware CV/MIDI activation marked **OUT OF SCOPE** (symbolic waveform SVGs retained as non-audio visualization).
- Visual System Intelligence documents preserved and cross-linked to implementation paths.

### Tests

- Unit coverage for vision provider determinism, candidate self-confirm rejection, inventory immutability, and `NOT_COMPUTABLE` generation without confirmed modules.
- Inventory gate tests for rack-backed generation and generate-bridge API fields.
- Inventory persistence, multi-image evidence upload, retention expiry, native bridge IDs.
- Acceptance (testcontainers): 11 passed on campaign branch.

### Database

- Alembic `20240929_visual_inventory_evidence`: `system_inventory_revisions`, `image_assets`, `classification_evidence_records`.

## 0.3.0 — Planned line

One-page Patch Book Generator implementation.

Planned scope includes versioned page contracts, deterministic semantic assembly, SVG-first technical diagrams, page-fit validation, accessible PDF/SVG/JSON/ZIP export, and manifest-bound release evidence.

No `v0.3.0` release tag exists at the time of this entry.

## 0.2.x — Retroactive canon-aligned MVP line

### Added

- Immutable user → rig → rig revision → run → patch library → patch hierarchy.
- Deterministic compiler contracts, canonical JSON, stable hashes, stage receipts, and artifact manifests.
- Canonical PatchGraph, five-phase PatchPlan, deterministic variations, and validation reporting.
- Canonical credits and exports API under `/api/canon/*`.
- Test-mode Stripe-style webhook and transactional ledger behavior.
- Instrument-bench workspace, graph/table accessibility pair, and light/dark themes.
- Security, operations, accessibility, canon-alignment, and continuation documentation.

### Changed

- Canonical UI export and credit clients migrated away from legacy frontend debit behavior.
- Historical social, publishing, leaderboard, and referral surfaces disabled by default.

### Known gaps

- Legacy acceptance and inventory paths remain partially present.
- Production deployment and live payments have not been authorized.
- Staging backup/restore, full operational, and production-readiness evidence remain incomplete.

This line includes work merged through PRs #47, #49, and subsequent documentation alignment. It is a descriptive lineage, not a claim that every `0.2.x` tag was issued.

## 0.1.x — Retroactive historical prototype line

Early PatchHive work explored rig ingestion, patch generation, exports, publishing, community, deployment packaging, and Abraxas bridge concepts. These surfaces vary in authority and maturity. Current ship authority comes from the canon-aligned documentation and active runtime classification, not historical root notes or disabled legacy modules.

No complete historical release sequence is asserted.
