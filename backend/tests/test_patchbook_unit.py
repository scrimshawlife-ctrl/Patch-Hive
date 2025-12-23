"""Unit tests for PatchBook export pipeline."""

from __future__ import annotations

from sqlalchemy.orm import Session

from patches.models import Patch
from racks.models import Rack

from export.patchbook.builder import build_patchbook_document, compute_patchbook_content_hash
from export.patchbook.models import PatchBookExportRequest, PATCHBOOK_TEMPLATE_VERSION
from export.patchbook.render_pdf import build_patchbook_pdf_bytes


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
    content_hash = compute_patchbook_content_hash(payload)

    document = build_patchbook_document(db_session, sample_rack_basic, [patch], content_hash)
    pdf_bytes = build_patchbook_pdf_bytes(document)
    pdf_bytes_repeat = build_patchbook_pdf_bytes(document)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
    assert pdf_bytes == pdf_bytes_repeat
    assert PATCHBOOK_TEMPLATE_VERSION.encode("utf-8") in pdf_bytes
    assert content_hash.encode("utf-8") in pdf_bytes
    assert b"CreationDate" not in pdf_bytes
