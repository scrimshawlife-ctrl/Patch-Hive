# Architecture

## Style

**Modular monolith** (FastAPI) + **React/Vite** SPA. Prefer in-process modules over microservices unless evidence demands otherwise.

## Trust boundary (visual system intelligence)

```text
Untrusted image/provider output
  → evidence records only
  → human confirmation
  → immutable SystemInventoryRevision
  → deterministic generation / export
```

Provider output **cannot** self-promote to `USER_CONFIRMED`.

## Canonical hierarchy

```text
User → Rig → immutable RigRevision → GenerationRun
  → exactly one PatchLibrary → GeneratedPatch
```

Mutable overlays: favorites, notes, tried flags.

## Key packages

See [repository_map.md](repository_map.md). Authoritative product docs: `docs/VISUAL_SYSTEM_INTELLIGENCE.md`, `docs/CANON.md`, `CURRENT_STATE.md`.

## Data

- SQLAlchemy models + Alembic migrations (`backend/alembic/`)
- Single migration head required for release gates
- Current head (post-#66): `20240929_visual_inventory_evidence`

## Determinism

- Fixed seed + versions → equivalent canonical JSON / hashes
- Native bridge IDs: `rig-rev-{content_hash}` / `gen-run-{id}-{hash}`
- Symbolic waveform SVG is visualization, not audio DSP

## Feature flags

Legacy social/publishing/leaderboards/referrals default **off** (`.env.example`).
