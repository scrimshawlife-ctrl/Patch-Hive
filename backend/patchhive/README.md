# PatchHive v1.0 — Canonical Subsystem

PatchHive is a deterministic compiler for modular rigs. It ingests evidence, resolves it against the
append-only Module Gallery, and emits canonical rig data, layouts, and patches with explicit
provenance and confidence.

## Photo Ingestion
1. `detect_modules_from_photo` wraps Gemini Vision behind a mockable client interface.
2. Detections produce `DetectedModule` artifacts with image evidence and confidence.

## Gallery Resolution
1. `resolve_modules` matches detections against the Module Gallery.
2. `ensure_module_specs` keeps the gallery append-only, adds provenance, and creates explicit stubs
   for missing modules without inventing specs.

## Rig Build
1. `build_canonical_rig` normalizes resolved modules, exposes explicit signal contracts, and
   materializes semi-normalled edges with `break_on_insert`.
2. `map_metrics` emits the `RigMetricsPacket` consumed by Abraxas.

## Layout Suggestion
`suggest_layouts` returns exactly three deterministic layouts (Beginner, Performance, Experimental),
with weighted scoring for reach, cable crossing, learning gradient, utility proximity, and
patch-template coverage.

## Patch Generation
`generate_patch` outputs:
* `PatchGraph` with explicit mode selections.
* `PatchPlan` with the mandatory ritual timeline (prep → threshold → peak → release → seal).
* `ValidationReport` and deterministic variations.

## Abraxas Interface
PatchHive exposes only `RigMetricsPacket` and `SymbolicPatchEnvelope` for symbolic interpretation.
PatchHive owns physical truth; Abraxas owns symbolic resonance. Neither overwrites the other.
