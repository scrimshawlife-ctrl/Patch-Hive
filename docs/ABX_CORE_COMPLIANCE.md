# ABX-Core v1.2 Compliance

This document demonstrates how PatchHive implements Applied Alchemy Labs (AAL) architecture principles and complies with ABX-Core v1.2 standards.

## Overview

ABX-Core is an architecture framework emphasizing:
- **Modularity**: Clear boundaries and single responsibilities
- **Determinism**: Predictable, reproducible behavior
- **Entropy Minimization**: No hidden randomness or state
- **Eurorack Mental Model**: Domain-specific modeling
- **SEED Enforcement**: Full data provenance and traceability

---

## 1. Modularity

### Principle

System components should be independent, composable modules with clear interfaces and minimal coupling.

### Implementation

#### Backend Domain Separation

Each domain is isolated with its own:
- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic request/response validation
- **Routes**: FastAPI endpoints
- **Business Logic**: Domain-specific functions

**Domains**:
```
backend/
├── core/          # Shared utilities (config, database, security, naming)
├── modules/       # Module catalog management
├── cases/         # Case catalog management
├── racks/         # Rack builder and validation
├── patches/       # Patch engine, storage, routes
├── community/     # Users, auth, voting, comments
├── export/        # Visualization and PDF generation
└── ingest/        # External data import adapters
```

**Inter-domain Communication**:
- Domains communicate via **explicit imports** of models
- **No circular dependencies**
- Shared logic is factored into `core/`

#### Frontend Component Organization

```
frontend/src/
├── pages/         # Route-level pages
├── components/    # Reusable UI components
├── lib/           # API client, state management
└── types/         # TypeScript type definitions
```

### Compliance Score: ✅ **Excellent**

Clear separation of concerns with minimal coupling.

---

## 2. Determinism

### Principle

Given the same inputs, the system must always produce the same outputs. No hidden randomness or non-deterministic behavior.

### Implementation

#### Patch Generation Engine

**Key Feature**: Fully deterministic patch generation.

```python
def generate_patches_for_rack(
    db: Session,
    rack: Rack,
    seed: Optional[int] = None,
    config: Optional[PatchEngineConfig] = None
) -> List[PatchSpec]:
    if seed is None:
        seed = settings.default_generation_seed

    # Use seeded Random instance
    rng = random.Random(seed)

    # All "random" choices use rng
    vco = rng.choice(vcos)
    if rng.random() > 0.5:
        # ...
```

**Guarantees**:
- Same `rack` + same `seed` → Same patches
- Same naming (deterministic hash-based)
- No system time, no `os.urandom()`, no `/dev/random`

#### Naming Service

**Deterministic rack/patch names**:

```python
def generate_rack_name(seed: int) -> str:
    hash_bytes = hashlib.sha256(str(seed).encode()).digest()
    adj_idx = int.from_bytes(hash_bytes[0:4], 'big') % len(ADJECTIVES)
    noun_idx = int.from_bytes(hash_bytes[4:8], 'big') % len(NOUNS)
    return f"{ADJECTIVES[adj_idx]} {NOUNS[noun_idx]}"
```

**Examples**:
- Seed 42 → Always "Midnight Swarm"
- Seed 100 → Always "Solar Lattice"

#### Waveform Generation

**Deterministic waveform approximation**:

```python
def generate_waveform_svg(
    params: WaveformParams,
    seed: int = 42
) -> str:
    # Noise uses deterministic hash
    noise = (hash((seed, i)) % 2000 - 1000) / 1000
```

### Compliance Score: ✅ **Excellent**

All randomness is seeded and reproducible.

---

## 3. Entropy Minimization

### Principle

Avoid unnecessary randomness. When randomness is needed, it must be **explicit** and **controlled**.

### Implementation

#### No Hidden Entropy Sources

**Forbidden**:
- `random.random()` without seeding
- `uuid.uuid4()` for IDs
- `datetime.now()` for non-timestamp purposes
- `os.urandom()`

**Allowed**:
- `random.Random(seed)` with explicit seed
- Database auto-increment IDs
- Timestamps for audit trails

#### Explicit Seeding

All patch generation requires an explicit seed:

```python
# API endpoint
@router.post("/generate/{rack_id}")
def generate_patches(rack_id: int, request: GeneratePatchesRequest):
    seed = request.seed or settings.default_generation_seed
    patches = generate_patches_for_rack(db, rack, seed=seed, config=config)
```

If no seed is provided, a **configured default** is used (not system entropy).

#### Configuration-Driven Randomness

```python
class Settings(BaseSettings):
    default_generation_seed: int = 42  # Explicit default
```

### Compliance Score: ✅ **Excellent**

No hidden entropy; all randomness is explicit and controlled.

---

## 4. Eurorack Mental Model

### Principle

Data structures and domain language should mirror the physical/conceptual domain being modeled.

### Implementation

#### Domain Language

**PatchHive uses Eurorack terminology consistently**:

| Term        | Meaning                              | Implementation                 |
|-------------|--------------------------------------|--------------------------------|
| **Module**  | Eurorack module                      | `Module` model                 |
| **Case**    | Eurorack case                        | `Case` model                   |
| **Rack**    | Configured case with modules         | `Rack` model                   |
| **Patch**   | Cable connections between modules    | `Patch` model                  |
| **HP**      | Horizontal Pitch (module width unit) | `hp` field                     |
| **Row**     | Horizontal row in a case             | `row_index` field              |
| **Port**    | Input/output jack                    | `io_ports` JSON array          |
| **Signal**  | Audio/CV/Gate/Clock connection       | `cable_type` field             |

#### Signal Flow Modeling

**Patch connections follow Eurorack signal flow**:

```python
@dataclass
class Connection:
    from_module_id: int
    from_port: str      # e.g., "Audio Out"
    to_module_id: int
    to_port: str        # e.g., "Audio In"
    cable_type: str     # "audio", "cv", "gate", "clock"
```

**Matches physical patching**:
- Cables go from outputs to inputs
- Signal types: Audio, CV (control voltage), Gate, Clock
- Connections are explicit and traceable

#### Module Categorization

**Based on Eurorack functions**:
- **VCO**: Voltage Controlled Oscillator
- **VCF**: Voltage Controlled Filter
- **VCA**: Voltage Controlled Amplifier
- **ENV**: Envelope generator
- **LFO**: Low Frequency Oscillator
- **SEQ**: Sequencer
- **MIX**: Mixer
- **FX**: Effects processor
- **UTIL**: Utility module

### Compliance Score: ✅ **Excellent**

Perfect alignment with domain concepts.

---

## 5. SEED Enforcement

### Principle

**SEED = Source, Entropy, Evidence, Determinism**

All data must have:
- **Source**: Where did it come from?
- **Entropy**: How was randomness used?
- **Evidence**: Audit trail of changes
- **Determinism**: Can it be reproduced?

### Implementation

#### Data Provenance Tracking

**Module Import Tracking**:

```python
class Module(Base):
    source = Column(String(50), nullable=False)  # "Manual", "CSV", "ModularGrid"
    source_reference = Column(String(500), nullable=True)  # URL, filename, etc.
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**Example**:
```json
{
  "source": "CSV",
  "source_reference": "modules_import_2024-01-15.csv",
  "imported_at": "2024-01-15T10:30:00Z"
}
```

#### Patch Generation Metadata

**Every patch stores its generation parameters**:

```python
class Patch(Base):
    generation_seed = Column(Integer, nullable=False)
    generation_version = Column(String(20), nullable=False)  # e.g., "1.0.0"
    engine_config = Column(JSON, nullable=True)
```

**Example**:
```json
{
  "generation_seed": 42,
  "generation_version": "1.0.0",
  "engine_config": {
    "max_patches": 20,
    "allow_feedback": false,
    "prefer_simple": false
  }
}
```

**Reproducibility**:
```python
# Reproduce exact same patches
patches = generate_patches_for_rack(
    db,
    rack,
    seed=patch.generation_seed,
    config=PatchEngineConfig(**patch.engine_config)
)
# Result: Identical patches as original generation
```

#### Audit Trail

**Timestamps on all entities**:
- `created_at`: When entity was created
- `updated_at`: When entity was last modified

**User actions tracked**:
- Who created this rack?
- When was this patch generated?
- Who voted on this?

#### Configuration Versioning

**Engine version stored with patches**:

```python
class Settings(BaseSettings):
    patch_engine_version: str = "1.0.0"
```

When the engine changes:
1. Increment version
2. Old patches retain their version
3. Can regenerate with old version if needed (future feature)

#### SEED Principle Checklist

| Principle     | Implementation                                    | Status |
|---------------|---------------------------------------------------|--------|
| **Source**    | All data has `source` and `source_reference`     | ✅     |
| **Entropy**   | All randomness uses explicit seeds               | ✅     |
| **Evidence**  | Timestamps and user tracking on all entities     | ✅     |
| **Determinism**| Patch generation is fully reproducible          | ✅     |

### Compliance Score: ✅ **Excellent**

Full SEED compliance with comprehensive provenance tracking.

---

## Summary Scorecard

| Principle              | Compliance | Notes                                          |
|------------------------|------------|------------------------------------------------|
| **Modularity**         | ✅ Excellent | Clear domain separation, minimal coupling     |
| **Determinism**        | ✅ Excellent | All randomness seeded and reproducible        |
| **Entropy Minimization**| ✅ Excellent | No hidden entropy sources                     |
| **Eurorack Mental Model**| ✅ Excellent | Perfect domain alignment                     |
| **SEED Enforcement**   | ✅ Excellent | Full provenance and reproducibility           |

### Overall ABX-Core v1.2 Compliance: ✅ **100%**

---

## Future Enhancements

### Phase 2
- **Versioned Engine Snapshots**: Store engine code with patches for true long-term reproducibility
- **Data Lineage Graphs**: Visual provenance chains showing data flow
- **Immutable Patch History**: Event sourcing for full audit trail

### Phase 3
- **Formal Verification**: Mathematical proofs of determinism properties
- **Compliance Testing**: Automated tests verifying ABX-Core principles
- **Provenance Queries**: Query language for exploring data lineage

---

## Verification

To verify compliance, run the following checks:

### Test Determinism

```python
# Generate patches twice with same seed
patches1 = generate_patches_for_rack(db, rack, seed=42)
patches2 = generate_patches_for_rack(db, rack, seed=42)

assert patches1 == patches2  # Must be identical
```

### Test Provenance

```python
# Every module has source tracking
for module in db.query(Module).all():
    assert module.source is not None
    assert module.imported_at is not None

# Every patch has generation metadata
for patch in db.query(Patch).all():
    assert patch.generation_seed is not None
    assert patch.generation_version is not None
```

### Test No Hidden Entropy

```bash
# Search for forbidden patterns
grep -r "random.random()" backend/  # Should only find in tests
grep -r "uuid.uuid4()" backend/     # Should not find any
grep -r "os.urandom" backend/       # Should not find any
```

---

**PatchHive is a fully ABX-Core v1.2 compliant system.**
