"""Content spine + fulfillment vertical tests."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from cases.models import Case
from community.models import User
from canon.exports import credit_balance, request_export
from canon.contracts import ExportRequest
from canon.fulfillment import fulfill_export, pack_dir_for_export
from canon.models import CanonicalCreditLedgerEntryRecord
from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule
from runs.bridge import ensure_legacy_run_export_bridge
from runs.models import Run


NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _seed_user_run_patches(db: Session) -> tuple[User, Run, object]:
    user = User(
        email="design-engine@example.com",
        username="design_engine",
        password_hash="hash",
    )
    case = Case(
        brand="PatchHive",
        name="Test Case",
        total_hp=104,
        rows=2,
        hp_per_row=[104, 104],
        source="test",
    )
    db.add_all([user, case])
    db.flush()

    rack = Rack(name="Rig", user_id=user.id, case_id=case.id)
    db.add(rack)
    db.flush()

    m1 = Module(brand="T", name="VCO", hp=12, module_type="VCO", source="test")
    m2 = Module(brand="T", name="VCA", hp=8, module_type="VCA", source="test")
    db.add_all([m1, m2])
    db.flush()
    db.add_all(
        [
            RackModule(rack_id=rack.id, module_id=m1.id, row_index=0, start_hp=0),
            RackModule(rack_id=rack.id, module_id=m2.id, row_index=0, start_hp=12),
        ]
    )
    db.flush()

    run = Run(rack_id=rack.id, status="completed")
    db.add(run)
    db.flush()

    for i in range(2):
        db.add(
            Patch(
                rack_id=rack.id,
                run_id=run.id,
                name=f"Patch {i}",
                category="Voice",
                description=f"Desc {i}",
                connections=[
                    {
                        "from_module_id": m1.id,
                        "from_port": "Audio Out",
                        "to_module_id": m2.id,
                        "to_port": "Audio In",
                        "cable_type": "audio",
                    }
                ],
                generation_seed=100 + i,
                generation_version="1.0.0",
            )
        )
    db.flush()

    bridge = ensure_legacy_run_export_bridge(db, run)
    db.add(
        CanonicalCreditLedgerEntryRecord(
            id="ledger-grant-design-1",
            user_id=user.id,
            delta=10,
            entry_type="grant",
            idempotency_key="grant-design-1",
            export_id=None,
            created_at=NOW,
        )
    )
    db.commit()
    return user, run, bridge


def test_fulfill_export_path_b_succeeds(db_session: Session, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("EXPORT_STORE_ROOT", str(tmp_path))
    # Reload settings is hard; patch module settings directly
    import core.config as config_mod

    monkeypatch.setattr(config_mod.settings, "export_store_root", str(tmp_path))
    monkeypatch.setattr(config_mod.settings, "export_dir", str(tmp_path))
    monkeypatch.setattr(config_mod.settings, "enable_canon_export_fulfillment", True)

    user, run, bridge = _seed_user_run_patches(db_session)
    assert credit_balance(db_session, user.id) == 10

    export = request_export(
        db_session,
        ExportRequest(
            request_id="req-design-1",
            user_id=user.id,
            source_run_id=bridge.source_run_id,
            source_rig_revision_id=bridge.rig_revision_id,
            formats=("pdf", "json"),
            license="personal",
            credit_cost=3,
            idempotency_key="idem-design-fulfill-1",
            requested_at=NOW,
        ),
        artifact_manifest_hash=bridge.artifact_manifest_hash,
        export_version="1.0.0",
    )
    db_session.commit()

    result = fulfill_export(db_session, export.id)
    db_session.commit()
    db_session.refresh(export)

    assert result.status == "succeeded", result
    assert export.status == "succeeded"
    assert export.composition_hash
    assert export.pack_manifest_hash
    assert export.library_content_hash
    pack = pack_dir_for_export(export.id)
    assert (pack / "PatchBook.pdf").exists()
    assert (pack / "technical" / "companion.txt").exists()
    assert (pack / "manifest" / "patch-book.json").exists()
    pdf = (pack / "PatchBook.pdf").read_bytes()
    assert pdf.startswith(b"%PDF")
    assert credit_balance(db_session, user.id) == 7

    # Idempotent second fulfill
    result2 = fulfill_export(db_session, export.id)
    assert result2.status == "succeeded"
    assert result2.composition_hash == result.composition_hash


def test_seal_orm_deterministic(db_session: Session) -> None:
    from export.patchbook.design.content_spine import seal_orm_patch_to_compilation

    user, run, bridge = _seed_user_run_patches(db_session)
    patch = db_session.query(Patch).filter(Patch.run_id == run.id).order_by(Patch.id).first()
    assert patch is not None
    a = seal_orm_patch_to_compilation(
        patch,
        source_run_id=bridge.source_run_id,
        source_rig_revision_id=bridge.rig_revision_id,
        rig_snapshot={"modules": []},
        position=0,
    )
    b = seal_orm_patch_to_compilation(
        patch,
        source_run_id=bridge.source_run_id,
        source_rig_revision_id=bridge.rig_revision_id,
        rig_snapshot={"modules": []},
        position=0,
    )
    assert a.canonical_hash_value() == b.canonical_hash_value()
    assert len(a.patch_graph.edges) == 1
    assert a.patch_plan.title == patch.name
