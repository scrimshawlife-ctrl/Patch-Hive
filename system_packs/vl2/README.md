# PatchHive VL2 System Pack

Reference patch collection for Voltage Lab 2 synthesizer system.

## Overview

This system pack contains 12 reference patches demonstrating core VL2 concepts and patch architectures. All patches are schema-validated and include explicit wiring definitions.

## Contents

- **Schema**: `schema/patchhive.schema.vl2.v1.json`
- **Ontology**: `ontology/` (roles, operations, tags)
- **Patches**: `patches/` (PHVL2-0001 through PHVL2-0012)
- **Tests**: `tests/validate-pack.mjs`

## Patch Categories

### Probabilistic (3 patches)
- **PHVL2-0002**: Stochastic Melodies - Chance sequencer with varying probabilities
- **PHVL2-0005**: Chaotic Rhythms - Brownian sequencing with probabilistic gating
- **PHVL2-0010**: Probabilistic Modulation - Random modulation routing

### Temporal (4 patches)
- **PHVL2-0003**: Polyrhythmic Layers - Multiple clock divisions
- **PHVL2-0006**: Phase Drift - Evolving phase relationships
- **PHVL2-0011**: Cyclic Interference - Prime-number temporal patterns

### Gestural (2 patches)
- **PHVL2-0004**: Expressive Touch - XY pad performance control
- **PHVL2-0007**: Gestural FM - Real-time FM parameter control

### Erosion → Reconstruction (2 patches)
- **PHVL2-0008**: Digital Erosion - Progressive bitcrushing
- **PHVL2-0009**: Harmonic Reconstruction - Sync-based harmonic alignment

### Other
- **PHVL2-0001**: Fundamental Oscillation - Basic architecture demo
- **PHVL2-0012**: Recursive Feedback Network - Complex feedback routing

## Validation

Run validation tests:

```bash
cd system_packs/vl2
npm install
npm test
```

Tests verify:
- Schema compliance (AJV)
- SHA-256 hash integrity
- Manifest accuracy

## Schema Version

All patches use schema version `vl2.v1` and validate against `patchhive.schema.vl2.v1.json`.

## Integration

This pack is designed for direct import into PatchHive:

```javascript
import manifest from './system_packs/vl2/pack.manifest.json';
```

The manifest provides:
- Patch metadata
- File paths
- SHA-256 hashes
- Schema references
- Ontology mappings
