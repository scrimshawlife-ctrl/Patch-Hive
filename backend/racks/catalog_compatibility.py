"""Bridge rack placement to catalog compatibility when a case was materialized."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from cases.compatibility import evaluate_catalog_compatibility
from cases.compatibility_schemas import CompatibilityModuleIn, CompatibilityRequest, CompatibilityResponse
from cases.models import Case
from racks.models import Rack, RackModule


def catalog_slug_for_case(case: Case) -> Optional[str]:
    meta = case.meta if isinstance(case.meta, dict) else {}
    slug = meta.get("catalog_slug")
    if isinstance(slug, str) and slug.strip():
        return slug.strip()
    return None


def revision_key_for_case(case: Case) -> Optional[str]:
    meta = case.meta if isinstance(case.meta, dict) else {}
    key = meta.get("catalog_revision_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def evaluate_rack_catalog_compatibility(
    db: Session,
    rack: Rack,
    *,
    plan_close_lid: bool = False,
) -> dict[str, Any]:
    """Return catalog compatibility for a rack, or an incomplete bridge report."""
    case = db.query(Case).filter(Case.id == rack.case_id).first()
    if case is None:
        return {
            "bridge_status": "conflict",
            "message": f"Legacy case_id {rack.case_id} not found",
            "catalog_slug": None,
            "compatibility": None,
        }

    slug = catalog_slug_for_case(case)
    if not slug:
        return {
            "bridge_status": "incomplete",
            "message": (
                "Case has no meta.catalog_slug. Materialize from the normalized catalog "
                "to enable catalog compatibility checks."
            ),
            "catalog_slug": None,
            "case_id": case.id,
            "compatibility": None,
        }

    rack_modules = db.query(RackModule).filter(RackModule.rack_id == rack.id).all()
    modules = [
        CompatibilityModuleIn(
            module_id=rm.module_id,
            row_index=rm.row_index,
            start_hp=rm.start_hp,
        )
        for rm in rack_modules
    ]
    request = CompatibilityRequest(
        revision_key=revision_key_for_case(case),
        modules=modules,
        plan_close_lid=plan_close_lid,
    )
    try:
        report: CompatibilityResponse = evaluate_catalog_compatibility(db, slug, request)
    except LookupError as exc:
        return {
            "bridge_status": "conflict",
            "message": str(exc),
            "catalog_slug": slug,
            "case_id": case.id,
            "compatibility": None,
        }

    return {
        "bridge_status": "ok",
        "message": "Catalog compatibility evaluated from materialized case link",
        "catalog_slug": slug,
        "case_id": case.id,
        "module_count": len(modules),
        "compatibility": report.model_dump(mode="json"),
    }
