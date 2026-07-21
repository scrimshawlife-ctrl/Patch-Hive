"""Preview API helper + Path A load after dual-write."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from cases.models import Case
from community.models import User
from export.patchbook.design.content_spine import load_patch_compilations
from export.patchbook.design.dual_write import dual_write_generated_patches
from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule
from runs.bridge import ensure_legacy_run_export_bridge
from runs.models import Run

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def test_path_a_load_after_dual_write(db_session: Session) -> None:
    user = User(username="path-a", email="path-a@example.com", password_hash="h")
    case = Case(brand="PH", name="C", total_hp=84, rows=1, hp_per_row=[84], source="test")
    db_session.add_all([user, case])
    db_session.flush()
    rack = Rack(name="R", user_id=user.id, case_id=case.id)
    db_session.add(rack)
    db_session.flush()
    m1 = Module(brand="T", name="A", hp=12, module_type="VCO", source="test")
    m2 = Module(brand="T", name="B", hp=8, module_type="VCA", source="test")
    db_session.add_all([m1, m2])
    db_session.flush()
    db_session.add_all(
        [
            RackModule(rack_id=rack.id, module_id=m1.id, row_index=0, start_hp=0),
            RackModule(rack_id=rack.id, module_id=m2.id, row_index=0, start_hp=12),
        ]
    )
    run = Run(rack_id=rack.id, status="completed")
    db_session.add(run)
    db_session.flush()
    patch = Patch(
        rack_id=rack.id,
        run_id=run.id,
        name="Path A Patch",
        category="Voice",
        description="sealed",
        connections=[
            {
                "from_module_id": m1.id,
                "from_port": "Out",
                "to_module_id": m2.id,
                "to_port": "In",
                "cable_type": "audio",
            }
        ],
        generation_seed=7,
        generation_version="1.0.0",
    )
    db_session.add(patch)
    db_session.flush()
    bridge = ensure_legacy_run_export_bridge(db_session, run)
    h = dual_write_generated_patches(db_session, bridge=bridge, patches=[patch])
    db_session.commit()
    assert h and len(h) == 64

    loaded = load_patch_compilations(
        db_session,
        source_run_id=bridge.source_run_id,
        source_rig_revision_id=bridge.rig_revision_id,
        artifact_manifest_hash=bridge.artifact_manifest_hash,
    )
    assert loaded.load_path == "generated_patches"
    assert len(loaded.items) == 1
    assert loaded.items[0].compilation.patch_plan.title == "Path A Patch"
    assert loaded.library_content_hash == h
