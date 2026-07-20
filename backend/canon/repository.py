"""Transactional persistence adapter for the immutable canonical hierarchy."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from canon.contracts import CanonicalRig, SCHEMA_VERSION, canonical_sha256
from canon.models import GenerationRunRecord, PatchLibraryRecord, RigRevisionRecord


def append_rig_revision(
    session: Session,
    *,
    rig_db_id: int,
    rig: CanonicalRig,
    previous_revision_id: str | None = None,
    created_at: datetime | None = None,
) -> RigRevisionRecord:
    """Append a rig revision; referenced prior revisions remain intact."""

    record = RigRevisionRecord(
        id=rig.rig_revision_id,
        rig_id=rig_db_id,
        previous_revision_id=previous_revision_id,
        schema_version=SCHEMA_VERSION,
        canonical_rig=rig.canonical_dict(),
        canonical_hash=rig.canonical_hash,
        created_at=created_at,
    )
    session.add(record)
    session.flush()
    return record


def create_run_with_library(
    session: Session,
    *,
    run_id: str,
    library_id: str,
    user_id: int,
    rig_revision_id: str,
    generator_version: str,
    generation_seed: int,
    normalized_input: object,
    artifact_manifest_hash: str,
    library_hash: str,
    created_at: datetime | None = None,
) -> tuple[GenerationRunRecord, PatchLibraryRecord]:
    """Create a new immutable run and its exactly-one library in one transaction."""

    run = GenerationRunRecord(
        id=run_id,
        user_id=user_id,
        rig_revision_id=rig_revision_id,
        schema_version=SCHEMA_VERSION,
        generator_version=generator_version,
        generation_seed=generation_seed,
        normalized_input_hash=canonical_sha256(normalized_input),
        created_at=created_at,
    )
    library = PatchLibraryRecord(
        id=library_id,
        run_id=run_id,
        artifact_manifest_hash=artifact_manifest_hash,
        canonical_hash=library_hash,
        created_at=created_at,
    )
    session.add_all((run, library))
    session.flush()
    return run, library
