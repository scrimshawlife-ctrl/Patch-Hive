"""Legacy Run → canonical export bridge.

MVP UI still lists integer ``runs`` rows. Canonical exports require
``generation_runs`` + ``rig_revisions`` FK targets and a 64-char manifest hash.

This module:
1. Derives stable bridge identifiers from legacy ``run_id`` / ``rack_id``
2. Ensures matching canon rows exist (idempotent upsert-by-id)
3. Powers enriched ``RunResponse`` fields so the FE does not invent IDs/hashes
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy.orm import Session

from canon.models import GenerationRunRecord, PatchLibraryRecord, RigRevisionRecord
from racks.models import Rack
from runs.models import Run


def legacy_rig_revision_id(rack_id: int) -> str:
    return f"legacy-rack-{int(rack_id)}"


def legacy_source_run_id(run_id: int) -> str:
    return f"legacy-run-{int(run_id)}"


def legacy_artifact_manifest_hash(run_id: int, rack_id: int) -> str:
    """Match historical FE bridge: sha256('patchhive:legacy-run:{run}:rig:{rack}')."""
    payload = f"patchhive:legacy-run:{int(run_id)}:rig:{int(rack_id)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_hash(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LegacyRunExportBridge:
    run_id: int
    rack_id: int
    rig_revision_id: str
    source_run_id: str
    artifact_manifest_hash: str
    export_bridge_ready: bool

    def as_export_body_fields(self) -> dict[str, str]:
        return {
            "source_run_id": self.source_run_id,
            "source_rig_revision_id": self.rig_revision_id,
            "artifact_manifest_hash": self.artifact_manifest_hash,
        }


def bridge_for_run(run: Run) -> LegacyRunExportBridge:
    run_id = int(run.id)  # type: ignore[arg-type]
    rack_id = int(run.rack_id)  # type: ignore[arg-type]
    return LegacyRunExportBridge(
        run_id=run_id,
        rack_id=rack_id,
        rig_revision_id=legacy_rig_revision_id(rack_id),
        source_run_id=legacy_source_run_id(run_id),
        artifact_manifest_hash=legacy_artifact_manifest_hash(run_id, rack_id),
        export_bridge_ready=False,
    )


def ensure_legacy_run_export_bridge(db: Session, run: Run) -> LegacyRunExportBridge:
    """Idempotently create canon hierarchy rows required for /api/canon/exports."""
    bridge = bridge_for_run(run)
    rack = db.get(Rack, run.rack_id)
    if rack is None:
        return bridge

    user_id = int(rack.user_id)  # type: ignore[arg-type]
    revision_id = bridge.rig_revision_id
    source_run_id = bridge.source_run_id
    library_id = f"library-{source_run_id}"
    manifest_hash = bridge.artifact_manifest_hash

    if db.get(RigRevisionRecord, revision_id) is None:
        db.add(
            RigRevisionRecord(
                id=revision_id,
                rig_id=bridge.rack_id,
                schema_version="patchhive.canon.v1",
                canonical_rig={
                    "bridge": "legacy-rack",
                    "rack_id": bridge.rack_id,
                },
                canonical_hash=_stable_hash(f"rig-revision:{revision_id}"),
            )
        )
        db.flush()

    if db.get(GenerationRunRecord, source_run_id) is None:
        db.add(
            GenerationRunRecord(
                id=source_run_id,
                user_id=user_id,
                rig_revision_id=revision_id,
                schema_version="patchhive.canon.v1",
                generator_version="1.0.0",
                generation_seed=bridge.run_id,
                normalized_input_hash=_stable_hash(f"generation-run:{source_run_id}"),
            )
        )
        db.flush()

    if db.get(PatchLibraryRecord, library_id) is None:
        db.add(
            PatchLibraryRecord(
                id=library_id,
                run_id=source_run_id,
                artifact_manifest_hash=manifest_hash,
                canonical_hash=_stable_hash(f"patch-library:{library_id}"),
            )
        )
        db.flush()

    return LegacyRunExportBridge(
        run_id=bridge.run_id,
        rack_id=bridge.rack_id,
        rig_revision_id=revision_id,
        source_run_id=source_run_id,
        artifact_manifest_hash=manifest_hash,
        export_bridge_ready=True,
    )
