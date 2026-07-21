# Visual System Intelligence

**Status:** Canon-compatible engineering specification  
**Scope:** Photo-assisted rig ingestion, system inventory, system-constrained patch generation, and photo-derived Patch Books

## 1. Product contract

PatchHive must analyze one or more photographs or screenshots of a user's modular, semi-modular, desktop, rack, pedal, or hybrid synthesizer system; classify visible devices and modules; construct an editable canonical inventory; and generate patches constrained to the confirmed capabilities of that system.

This capability extends the existing rig-ingestion and patch-generation architecture. It is not a parallel subsystem and does not permit nondeterministic vision output to mutate canonical rig state.

## 2. Trust boundary

```text
Photo / Screenshot Intake
  -> untrusted vision evidence acquisition
  -> image quality and region assessment
  -> module/device candidate detection
  -> Device Registry retrieval and candidate ranking
  -> user confirmation or explicit unresolved state
  -> immutable CanonicalRigRevision
  -> deterministic SystemCapabilityGraph
  -> deterministic patch generation and validation
  -> deterministic Patch Book compilation
```

Vision providers propose evidence only. Canonical state is created only after schema validation and confirmation-policy evaluation.

## 3. Supported inputs

- rack overview photographs
- close-up module photographs
- multiple angles of the same system
- Eurorack, Buchla-format, 5U, semi-modular, desktop, rack, pedalboard, and hybrid systems
- screenshots of virtual modular systems
- photographs containing visible patch cables
- partially occluded, rotated, perspective-distorted, reflective, or low-light images

## 4. Canonical contracts

The versioned system model must include:

- `SystemImage`
- `ImageRegion`
- `DeviceCandidate`
- `ModuleCandidate`
- `PhysicalPosition`
- `PortCandidate`
- `ControlCandidate`
- `CableCandidate`
- `ConnectionCandidate`
- `ClassificationEvidence`
- `ConfirmationDecision`
- `SystemCapabilityGraph`
- `SystemInventoryRevision`

Every candidate and resolved entity must carry:

- evidence reference
- provenance status
- confidence and calibration version
- provider/model identity
- candidate alternatives
- confirmation state
- schema and registry version

Required provenance statuses:

- `OBSERVED`
- `INFERRED`
- `USER_CONFIRMED`
- `REJECTED`
- `UNKNOWN`
- `NOT_COMPUTABLE`

## 5. Recognition pipeline

1. Validate file type, dimensions, metadata policy, and authorization.
2. Re-encode images and remove untrusted metadata.
3. Assess blur, glare, occlusion, perspective, and coverage.
4. Detect racks, devices, panels, and module boundaries.
5. Extract logos, labels, panel text, dimensions, and visual embeddings.
6. Retrieve and rank Device Registry candidates.
7. Detect controls, ports, displays, switches, and visible cables where supported.
8. Reconcile candidates across multiple images.
9. Present confidence, alternatives, evidence, and unresolved fields to the user.
10. Create a canonical inventory revision only from confirmed or policy-accepted records.

## 6. Module and device classification

For each detected item PatchHive should attempt to resolve:

- manufacturer
- product name
- revision or generation
- format and dimensions
- functional categories
- inputs and outputs
- controls and modes
- signal and voltage domains
- modulation and clock capabilities
- MIDI, USB, CV, gate, trigger, audio, and digital connectivity
- firmware variants where material
- Device Registry match and alternatives

Unknown-class rejection is mandatory. The system must prefer `UNKNOWN` over a forced low-confidence classification.

## 7. Patch-cable reconstruction

Visible cable analysis is an evidence-producing P1 capability. It must:

- detect cable segments and probable endpoints
- associate endpoints with resolved ports
- preserve ambiguity at crossings and occlusions
- infer direction and signal class only when supported by device specifications and visible evidence
- identify probable feedback paths and surface bounded warnings
- produce an editable connection graph

No obscured endpoint may be labeled `OBSERVED`. Ambiguous paths remain `INFERRED`, `UNKNOWN`, or `NOT_COMPUTABLE` until confirmed.

## 8. User confirmation

Users must be able to:

- confirm, reject, replace, or defer each uncertain classification
- choose among ranked candidates
- add an unknown device manually
- correct physical position
- resolve duplicate detections
- confirm or reject inferred cable endpoints
- create a new immutable inventory revision after correction

User-confirmed facts supersede provider inference while preserving original evidence.

## 9. Hardware-constrained patch suggestions

Patch generation must use the exact confirmed `SystemCapabilityGraph`. Each suggestion must include:

- required modules or devices
- ordered source-to-destination connections
- initial control positions and modes
- setup and calibration prerequisites
- expected sonic behavior and listening cues
- performance controls and variations
- validation findings and bounded safety warnings
- provenance and confidence
- explicit substitutions when the exact topology is unavailable

PatchHive should prefer patches achievable with the user's existing system. Commercial recommendations are separate, opt-in, and subordinate to no-purchase solutions.

## 10. Photo-derived Patch Books

A confirmed photographed system may generate a Patch Book containing:

- system overview and confirmed inventory
- rack or workspace layout
- module glossary
- system-specific patch recipes
- deterministic cable diagrams and ordered connection tables
- starting settings, listening cues, variations, and troubleshooting
- confidence and unresolved-data annotations
- source image references, rig revision, run identity, and revision history

The one-patch-per-page publishing invariant remains binding.

## 11. Security and privacy

- Treat image metadata, OCR text, filenames, and embedded prompts as untrusted.
- Re-encode uploads before provider or worker processing.
- Apply MIME sniffing, size limits, decompression-bomb controls, and malware scanning.
- Store only the minimum image data required by the user's retention choice.
- Bind derived evidence to source-image hashes without exposing private image URLs.
- Never expose provider prompts, credentials, or hidden chain-of-thought.
- Support image deletion while preserving legally required audit and derived-artifact lineage where applicable.

## 12. Evaluation gates

Track at minimum:

- region and module detection precision/recall
- manufacturer and exact-model top-1/top-k accuracy
- unknown-class rejection quality
- confidence calibration error
- multi-photo reconciliation accuracy
- port detection accuracy
- cable endpoint and connection-graph accuracy
- user correction rate
- time to confirmed inventory
- generated-patch validation pass rate
- percentage of suggestions requiring unavailable hardware

A capability is not production-ready until evaluated against a versioned, representative, legally usable dataset with retained receipts.

## 13. Delivery priority

### P0

- image upload and quality assessment
- module/device candidate detection
- manufacturer/model resolution
- editable confirmation workflow
- canonical system inventory
- system-constrained patch suggestions

### P1

- multi-photo reconciliation
- rack-layout reconstruction
- control and port detection
- visible cable endpoint inference
- photo-derived Patch Book generation

### P2

- guided live-camera capture
- advanced layout optimization
- opt-in purchase recommendations
- community system similarity

## 14. Required integration points

This contract must remain aligned with:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/PATCH_ENGINE.md`
- `docs/PATCH_BOOK_GENERATOR.md`
- `docs/CONTINUATION.md`
- `docs/ROADMAP.md`
- `docs/PRODUCTION_READINESS.md`
- `docs/CANON_ALIGNMENT.md`

When those documents conflict, the repository's explicit canon and current-state authority rules determine which statement governs. Contradictions must be resolved through a versioned ADR or canon update rather than silently duplicated.

## 15. Implementation pointers (repository)

These code surfaces implement the trust boundary without replacing this contract:

| Concern | Path |
|---------|------|
| Secure image prep | `backend/evidence/images.py` |
| Provider-neutral adapter | `backend/evidence/vision_provider.py` |
| Visual contracts | `backend/canon/visual_contracts.py` |
| Inventory + generation gate | `backend/canon/inventory.py` |
| Provider cannot self-confirm (runes) | `backend/canon/runes.py` `detect_modules` |
| Audit receipts | `docs/evidence/` |

Signal type `audio` on ports/cables is **domain metadata**. Audio processing remains out of scope.
