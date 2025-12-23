"""Unit tests for PatchBook export pipeline."""

from __future__ import annotations

from sqlalchemy.orm import Session

from patches.models import Patch
from racks.models import Rack

from export.patchbook.build import build_patchbook_pdf_bytes_from_payload
from export.patchbook.models import PatchBookExportRequest, PATCHBOOK_TEMPLATE_VERSION
from export.patchbook import pdf_meta


def _create_patch(db_session: Session, rack: Rack) -> Patch:
    patch = Patch(
        rack_id=rack.id,
        run_id=None,
        name="Test Patch",
        category="Voice",
        description="Test patch description",
        connections=[
            {
                "from_module_id": rack.modules[0].module_id,
                "from_port": "Audio Out",
                "to_module_id": rack.modules[1].module_id,
                "to_port": "Audio In",
                "cable_type": "audio",
            }
        ],
        generation_seed=42,
        generation_version="1.0.0",
        engine_config={"parameters": {str(rack.modules[0].module_id): {"Tune": "12 o'clock"}}},
    )
    db_session.add(patch)
    db_session.commit()
    db_session.refresh(patch)
    return patch


def test_build_patchbook_pdf_bytes_deterministic(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    patch = _create_patch(db_session, sample_rack_basic)

    payload = PatchBookExportRequest(rack_id=sample_rack_basic.id, patch_ids=[patch.id])
    pdf_bytes, content_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)
    pdf_bytes_repeat, repeat_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 10_000
    assert content_hash == repeat_hash
    assert PATCHBOOK_TEMPLATE_VERSION.encode("utf-8") in pdf_bytes
    assert content_hash.encode("utf-8") in pdf_bytes
    assert b"CreationDate" not in pdf_bytes


def test_patchbook_hash_stable_with_metadata_variation(
    db_session: Session,
    sample_rack_basic: Rack,
    monkeypatch,
) -> None:
    patch = _create_patch(db_session, sample_rack_basic)
    payload = PatchBookExportRequest(rack_id=sample_rack_basic.id, patch_ids=[patch.id])

    _, first_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)
    monkeypatch.setattr(pdf_meta, "apply_deterministic_pdf_metadata", lambda *args, **kwargs: None)
    _, second_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)

    assert first_hash == second_hash
