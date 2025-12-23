from __future__ import annotations

from sqlalchemy.orm import Session

from patches.models import Patch
from racks.models import Rack

from .builder import build_patchbook_document
from .content_hash import compute_patchbook_content_hash
from .contract_check import assert_patchbook_contract
from .models import PatchBookExportRequest, PATCHBOOK_TEMPLATE_VERSION
from .render_pdf import build_patchbook_pdf_bytes


def build_patchbook_pdf_bytes_from_payload(
    db: Session,
    payload: PatchBookExportRequest,
) -> tuple[bytes, str]:
    if not payload.rack_id and not payload.patch_ids:
        raise ValueError("rack_id or patch_ids required")

    patches_query = db.query(Patch)
    if payload.patch_ids:
        patches_query = patches_query.filter(Patch.id.in_(payload.patch_ids))
        patches = patches_query.all()
        if not patches:
            raise ValueError("Patches not found")
        rack_id = payload.rack_id or patches[0].rack_id
        rack = db.query(Rack).filter(Rack.id == rack_id).first()
    else:
        rack = db.query(Rack).filter(Rack.id == payload.rack_id).first()
        patches = db.query(Patch).filter(Patch.rack_id == payload.rack_id).all()

    if not rack:
        raise ValueError("Rack not found")
    if not patches:
        raise ValueError("No patches available for rack")

    document = build_patchbook_document(db, rack, patches)
    content_hash = compute_patchbook_content_hash(
        document.model_dump(mode="json"),
        PATCHBOOK_TEMPLATE_VERSION,
    )
    document.content_hash = content_hash

    assert_patchbook_contract(document)

    pdf_bytes = build_patchbook_pdf_bytes(document)
    return pdf_bytes, content_hash
