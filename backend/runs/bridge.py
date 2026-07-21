"""Legacy Run → canonical export bridge.

MVP UI still lists integer ``runs`` rows. Canonical exports require
``generation_runs`` + ``rig_revisions`` FK targets and a 64-char manifest hash.

This module:
1. Derives stable bridge identifiers from legacy ``run_id`` / ``rack_id``
2. Snapshots rack module layout into ``RigRevisionRecord.canonical_rig`` + content hash
3. Ensures matching canon rows exist (idempotent upsert-by-id)
4. Powers enriched ``RunResponse`` fields so the FE does not invent IDs/hashes
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from canon.models import GenerationRunRecord, PatchLibraryRecord, RigRevisionRecord
from racks.models import Rack, RackModule
from runs.models import Run

RACK_SNAPSHOT_SCHEMA = "patchhive.rack-snapshot.v1"


def legacy_rig_revision_id(rack_id: int) -> str:
    return f"legacy-rack-{int(rack_id)}"


def legacy_source_run_id(run_id: int) -> str:
    return f"legacy-run-{int(run_id)}"


def _sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_hash(label: str) -> str:
    return _sha256_hex(label)


def build_rack_content_snapshot(db: Session, rack: Rack) -> dict[str, Any]:
    """Deterministic layout snapshot for RigRevision.canonical_rig (matrix slice C)."""
    rack_id = int(rack.id)  # type: ignore[arg-type]
    case_id = int(rack.case_id)  # type: ignore[arg-type]
    rows = (
        db.query(RackModule)
        .filter(RackModule.rack_id == rack_id)
        .order_by(RackModule.row_index.asc(), RackModule.start_hp.asc(), RackModule.module_id.asc())
        .all()
    )
    modules = [
        {
            "module_id": int(rm.module_id),  # type: ignore[arg-type]
            "row_index": int(rm.row_index),  # type: ignore[arg-type]
            "start_hp": int(rm.start_hp),  # type: ignore[arg-type]
        }
        for rm in rows
    ]
    return {
        "schema": RACK_SNAPSHOT_SCHEMA,
        "bridge": "legacy-rack",
        "rack_id": rack_id,
        "case_id": case_id,
        "modules": modules,
    }


def rack_content_hash(snapshot: dict[str, Any]) -> str:
    """SHA-256 over canonical JSON of the rack snapshot (includes rack_id → unique)."""
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha256_hex(encoded)


def legacy_artifact_manifest_hash(
    run_id: int, rack_id: int, content_hash: str | None = None
) -> str:
    """Export artifact hash. Prefer content-bound form when snapshot hash is known."""
    if content_hash:
        payload = (
            f"patchhive:legacy-run:{int(run_id)}:rig:{int(rack_id)}:content:{content_hash}"
        )
    else:
        # Historical FE parity when no DB snapshot is available yet.
        payload = f"patchhive:legacy-run:{int(run_id)}:rig:{int(rack_id)}"
    return _sha256_hex(payload)


@dataclass(frozen=True)
class LegacyRunExportBridge:
    run_id: int
    rack_id: int
    rig_revision_id: str
    source_run_id: str
    artifact_manifest_hash: str
    export_bridge_ready: bool
    content_hash: str | None = None

    def as_export_body_fields(self) -> dict[str, str]:
        return {
            "source_run_id": self.source_run_id,
            "source_rig_revision_id": self.rig_revision_id,
            "artifact_manifest_hash": self.artifact_manifest_hash,
        }


def bridge_for_run(run: Run, content_hash: str | None = None) -> LegacyRunExportBridge:
    run_id = int(run.id)  # type: ignore[arg-type]
    rack_id = int(run.rack_id)  # type: ignore[arg-type]
    return LegacyRunExportBridge(
        run_id=run_id,
        rack_id=rack_id,
        rig_revision_id=legacy_rig_revision_id(rack_id),
        source_run_id=legacy_source_run_id(run_id),
        artifact_manifest_hash=legacy_artifact_manifest_hash(run_id, rack_id, content_hash),
        export_bridge_ready=False,
        content_hash=content_hash,
    )


def ensure_legacy_run_export_bridge(db: Session, run: Run) -> LegacyRunExportBridge:
    """Idempotently create/update canon hierarchy rows required for /api/canon/exports."""
    rack = db.get(Rack, run.rack_id)
    if rack is None:
        return bridge_for_run(run)

    snapshot = build_rack_content_snapshot(db, rack)
    content_hash = rack_content_hash(snapshot)
    bridge = bridge_for_run(run, content_hash=content_hash)

    user_id = int(rack.user_id)  # type: ignore[arg-type]
    revision_id = bridge.rig_revision_id
    source_run_id = bridge.source_run_id
    library_id = f"library-{source_run_id}"
    manifest_hash = bridge.artifact_manifest_hash

    existing_rev = db.get(RigRevisionRecord, revision_id)
    if existing_rev is None:
        db.add(
            RigRevisionRecord(
                id=revision_id,
                rig_id=bridge.rack_id,
                schema_version="patchhive.canon.v1",
                canonical_rig=snapshot,
                canonical_hash=content_hash,
            )
        )
        db.flush()
    else:
        # Keep stable revision id (legacy-rack-*); refresh content hash when layout changes.
        if str(existing_rev.canonical_hash) != content_hash:
            existing_rev.canonical_rig = snapshot
            existing_rev.canonical_hash = content_hash
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
                normalized_input_hash=_stable_hash(
                    f"generation-run:{source_run_id}:content:{content_hash}"
                ),
            )
        )
        db.flush()

    if db.get(PatchLibraryRecord, library_id) is None:
        db.add(
            PatchLibraryRecord(
                id=library_id,
                run_id=source_run_id,
                artifact_manifest_hash=manifest_hash,
                canonical_hash=_stable_hash(f"patch-library:{library_id}:{manifest_hash}"),
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
        content_hash=content_hash,
    )
