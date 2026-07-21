# Computer Vision Evaluation Protocol

Status: CANON-ALIGNED ENGINEERING SPECIFICATION

## Purpose

Define how PatchHive measures visual-system analysis without overstating accuracy. No production-readiness claim is valid without a versioned representative dataset, an exact source SHA, model and pipeline identity, and retained results.

## Evaluation objects

Evaluate independently:

- image quality assessment
- rack and system-region detection
- module/device detection
- manufacturer classification
- exact-model classification
- revision classification
- unknown-device rejection
- OCR and panel-text extraction
- port detection and labeling
- control detection and labeling
- multi-photo reconciliation
- visible cable detection
- cable endpoint association
- connection-graph reconstruction
- confidence calibration
- user correction burden
- hardware-constrained patch validity

## Dataset structure

Each evaluation case must include:

```yaml
case_id:
dataset_version:
license_and_consent:
image_assets:
scene_conditions:
ground_truth_inventory:
ground_truth_regions:
ground_truth_ports:
ground_truth_controls:
ground_truth_connections:
annotation_status:
reviewers:
```

Dataset partitions:

- development
- validation
- locked test
- adversarial and degraded-image set
- unknown/open-set set

The locked test set must not be used for prompt, threshold, or model tuning.

## Required diversity

Include variation across:

- manufacturers and model families
- panel colors and alternate revisions
- rack sizes and densities
- mixed hardware formats
- image angles and perspective
- lighting, glare, shadows, and reflections
- cable density and crossings
- occlusion
- image compression and blur
- partial systems and close-ups
- duplicated modules
- unknown and custom modules
- virtual modular screenshots where supported

A dataset dominated by clean catalog images is not representative of user-system photographs.

## Metrics

### Detection

- precision
- recall
- F1
- intersection over union
- average precision at declared thresholds

### Classification

- manufacturer top-1 accuracy
- exact-model top-1 accuracy
- top-k candidate recall
- revision accuracy
- unknown rejection precision and recall
- confusion matrix by manufacturer and module family

### Ports and controls

- detection precision and recall
- label accuracy
- direction and signal-class accuracy
- normalized localization error

### Connections

- cable detection precision and recall
- source endpoint accuracy
- destination endpoint accuracy
- full edge accuracy
- graph precision and recall
- ambiguous-route rate

### Calibration

- expected calibration error
- Brier score
- reliability plots
- accuracy by confidence bucket
- selective accuracy at abstention thresholds

### Product metrics

- user correction rate
- median corrections per system
- time to confirmed inventory
- percentage resolved without escalation
- hosted calls per confirmed system
- mean provider cost per confirmed system
- patch validation pass rate after confirmation

## Provenance classes

Evaluation output must preserve:

- `OBSERVED`
- `INFERRED`
- `USER_CONFIRMED`
- `REJECTED`
- `UNKNOWN`
- `NOT_COMPUTABLE`

An inferred cable route is never scored as an observed route unless endpoints are visible in ground truth.

## Test execution receipt

Every evaluation run must record:

```yaml
repository_sha:
branch:
dataset_version:
dataset_hash:
provider:
model:
model_version:
pipeline_version:
prompt_version:
registry_snapshot:
thresholds:
seed:
environment:
started_at:
completed_at:
metrics:
failures:
artifacts:
```

## Acceptance thresholds

Thresholds must be set from product risk and revised only through a documented decision. Before representative data exists, thresholds and readiness remain `NOT_COMPUTABLE`.

Minimum policy behavior regardless of measured accuracy:

- low-confidence identity requires confirmation
- unresolved required technical data blocks executable patch generation
- unknown devices remain unknown
- provider output cannot directly create canonical inventory
- cable inference abstains when endpoints are ambiguous
- manual fallback remains available

## Regression policy

A model, prompt, registry, scoring, or pipeline change requires evaluation against the locked test set. Regressions must be reported by capability and important cohort, not hidden inside a single aggregate score.

Block release when:

- exact-model recognition materially regresses
- unknown rejection weakens beyond policy threshold
- calibration worsens enough to make confirmation thresholds unreliable
- cable endpoint false positives increase beyond the accepted safety boundary
- deterministic normalization or receipts change unexpectedly

## Human review quality

Ground truth for ambiguous images requires at least two reviewers or one reviewer plus authoritative registry evidence. Disagreements must remain recorded and may be labeled `NOT_COMPUTABLE`.

## Privacy

Evaluation images require explicit rights and consent. Remove or mask faces, addresses, serial numbers, documents, screens, and unrelated private content when they are not necessary for evaluation.

## Reporting

Publish:

- aggregate metrics
- cohort metrics
- confusion matrices
- calibration results
- representative failures
- abstention behavior
- cost and latency distributions
- known dataset limitations

Never publish a bare accuracy percentage without dataset version, sample count, cohort coverage, and exact system identity.
