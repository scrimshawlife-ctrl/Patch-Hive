# ADR 0001: Canonical immutable hierarchy

Status: accepted.

PatchHive uses `User → Rig → RigRevision → GenerationRun → PatchLibrary → GeneratedPatch`. Rig/module revisions, runs, libraries, generated patches, stage receipts, manifests, ledger entries, and admin audit events are append-only. A run owns exactly one library through a unique foreign key. Regeneration creates a new run. User notes, favorite, and tried state are a separate mutable overlay.

The canonical domain is independent of FastAPI and SQLAlchemy. Transport contracts use frozen Pydantic models and byte-stable canonical JSON. SQLAlchemy classes are persistence adapters. Provider detection is evidence acquisition and cannot directly modify canonical truth.

This choice preserves reproducibility, provenance, auditability, and retry safety at the cost of additional rows and explicit revision selection.
