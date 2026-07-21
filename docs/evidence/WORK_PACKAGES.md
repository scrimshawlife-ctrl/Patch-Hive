# Work packages — Visual System Intelligence campaign

## WP-01 — Baseline and audit receipt

```yaml
work_package: WP-01
objective: Pin baseline SHA, toolchain, audio drift, capability matrix
files:
  - docs/evidence/BASELINE_RECEIPT.yaml
  - docs/evidence/AUDIO_DRIFT_CLASSIFICATION.md
  - docs/evidence/VISUAL_CAPABILITY_MATRIX.md
  - docs/evidence/PRODUCTION_READINESS_MATRIX.md
dependencies: []
implementation_steps:
  - Clone main, record SHA and env
  - Search audio/DSP terms; classify
  - Inventory VSI capabilities
tests: none (docs)
acceptance_criteria:
  - Baseline receipt complete
  - No silent deletion of legitimate audio signal vocabulary
risks: docs drift if HEAD moves without update
rollback: delete evidence docs
estimated_complexity: S
status: DONE
```

## WP-02 — Provider-neutral vision evidence adapter

```yaml
work_package: WP-02
objective: Define VisionEvidenceProvider with mock + fixture adapters
files:
  - backend/evidence/vision_provider.py
  - backend/evidence/images.py
  - backend/tests/unit/test_vision_provider_and_quality.py
dependencies: WP-01
implementation_steps:
  - Protocol for quality, regions, devices, classify, ports, controls, cables
  - MockDeterministicVisionProvider
  - RecordedFixtureVisionProvider
  - Local quality assessment after re-encode
tests:
  - deterministic packet equality
  - tiny image NOT_COMPUTABLE
  - local quality reject undersized
acceptance_criteria:
  - CI has zero live model calls
  - candidates cannot be USER_CONFIRMED
risks: mock quality scores may be misread as calibration — document clearly
rollback: remove vision_provider module + tests
estimated_complexity: M
status: DONE
```

## WP-03 — Visual contracts and inventory constraints

```yaml
work_package: WP-03
objective: Immutable inventory + capability graph + patch constraint gate
files:
  - backend/canon/visual_contracts.py
  - backend/canon/inventory.py
  - backend/tests/unit/test_visual_system_intelligence.py
dependencies: WP-02
implementation_steps:
  - ResolutionStatus + ClassificationCandidate + ConfirmationDecision
  - SystemInventoryRevision.seal()
  - enforce_confirmed_inventory_constraints
  - preserve detect_modules self-confirm rejection
tests:
  - self-confirm forbidden
  - obscured cable not OBSERVED
  - inventory hash stability
  - NOT_COMPUTABLE without confirmed modules
  - UNCONFIRMED_MODULE on ghost instances
acceptance_criteria:
  - generation gate fails closed
  - unresolved candidates excluded from inventory items
risks: dual vocabulary EpistemicStatus vs ResolutionStatus — document mapping
rollback: remove modules + tests
estimated_complexity: M
status: DONE
```

## WP-04 — Canon documentation alignment

```yaml
work_package: WP-04
objective: Align docs; preserve VSI docs; remove audio-simulation future claims
files:
  - README.md
  - CURRENT_STATE.md
  - CHANGELOG.md
  - docs/ARCHITECTURE.md
  - docs/DATA_MODEL.md
  - docs/PATCH_ENGINE.md
  - docs/ROADMAP.md
  - docs/SECURITY.md
  - docs/CONTINUATION.md
  - docs/CANON_ALIGNMENT.md
  - docs/PRODUCTION_READINESS.md
  - docs/VISUAL_SYSTEM_INTELLIGENCE.md (cross-links only)
dependencies: WP-01..03
implementation_steps:
  - Update HEAD/status tables
  - Cross-link VSI contracts implementation
  - Mark audio simulation OUT OF SCOPE
tests: none
acceptance_criteria:
  - No contradictory "audio simulation planned" as product work
  - VSI documents preserved not replaced
risks: SHA tables stale after next merge
rollback: git revert docs commits
estimated_complexity: S
status: DONE
```

## WP-05 — Wire inventory gate into generate API

```yaml
work_package: WP-05
objective: Bind confirmed rack inventory to generate_patches_with_ir + API response
files:
  - backend/patches/inventory_gate.py
  - backend/patches/engine.py
  - backend/patches/routes.py
  - backend/patches/schemas.py
  - backend/core/provenance.py
  - backend/tests/unit/test_inventory_gate.py
  - backend/tests/api/test_generate_bridge.py
dependencies: WP-03
implementation_steps:
  - Treat placed rack modules as manual USER_CONFIRMED inventory
  - NOT_COMPUTABLE when rack has no modules
  - Filter patches whose cables leave confirmed catalog module set
  - Surface inventory_revision_id / gate code / generation_status on generate response
  - Persist free-form provenance metrics via metrics.extra
status: DONE (this continuation execution)
estimated_complexity: M
```

## WP-06 — Persist inventory revisions

```yaml
work_package: WP-06
objective: Alembic tables for system_inventory_revisions + evidence assets
files:
  - backend/alembic/versions/20240929_visual_inventory_evidence.py
  - backend/canon/models.py
  - backend/canon/inventory_persist.py
  - backend/evidence/routes.py
  - backend/evidence/retention.py
dependencies: WP-03, WP-05
status: DONE
estimated_complexity: L
```

## WP-07 — Native bridge IDs

```yaml
work_package: WP-07
objective: Drop legacy-rack/run namespace from ensure_legacy_run_export_bridge writers
files:
  - backend/runs/bridge.py
  - tests for runs/generate/canon runs
  - frontend Playwright mocks
status: DONE
```
