"""Unit tests for legacy run export bridge id/hash helpers + rack content snapshot."""

from __future__ import annotations

from sqlalchemy.orm import Session

from canon.models import RigRevisionRecord
from modules.models import Module
from racks.models import Rack, RackModule
from runs.bridge import (
    build_rack_content_snapshot,
    ensure_legacy_run_export_bridge,
    legacy_artifact_manifest_hash,
    legacy_rig_revision_id,
    legacy_source_run_id,
    rack_content_hash,
)
from runs.models import Run


def test_legacy_bridge_ids_are_stable() -> None:
    assert legacy_rig_revision_id(7) == "legacy-rack-7"
    assert legacy_source_run_id(12) == "legacy-run-12"
    assert len(legacy_artifact_manifest_hash(12, 7)) == 64
    assert legacy_artifact_manifest_hash(12, 7) == legacy_artifact_manifest_hash(12, 7)


def test_content_bound_manifest_differs_from_historical() -> None:
    historical = legacy_artifact_manifest_hash(12, 7)
    content = legacy_artifact_manifest_hash(12, 7, content_hash="abc")
    assert historical != content
    assert len(content) == 64


def test_rack_snapshot_hash_changes_with_layout(
    db_session: Session,
    sample_rack_basic: Rack,
    sample_effect: Module,
) -> None:
    snap1 = build_rack_content_snapshot(db_session, sample_rack_basic)
    h1 = rack_content_hash(snap1)
    assert snap1["schema"] == "patchhive.rack-snapshot.v1"
    assert len(snap1["modules"]) >= 1

    db_session.add(
        RackModule(
            rack_id=sample_rack_basic.id,
            module_id=sample_effect.id,
            row_index=1,
            start_hp=0,
        )
    )
    db_session.commit()

    snap2 = build_rack_content_snapshot(db_session, sample_rack_basic)
    h2 = rack_content_hash(snap2)
    assert h1 != h2

    run = Run(rack_id=sample_rack_basic.id, status="completed")
    db_session.add(run)
    db_session.commit()

    bridge = ensure_legacy_run_export_bridge(db_session, run)
    db_session.commit()
    rev = db_session.get(RigRevisionRecord, bridge.rig_revision_id)
    assert rev is not None
    assert str(rev.canonical_hash) == h2
    assert bridge.content_hash == h2
    assert len(bridge.artifact_manifest_hash) == 64
    # Content-bound manifest must differ from historical run-only form.
    assert bridge.artifact_manifest_hash != legacy_artifact_manifest_hash(
        bridge.run_id, bridge.rack_id
    )
