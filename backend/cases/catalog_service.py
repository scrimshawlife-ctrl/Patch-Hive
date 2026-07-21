"""Query helpers for the normalized modular case catalog read API."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from cases.models import (
    CaseCatalog,
    CaseFeature,
    CasePowerSystem,
    CasePrice,
    CaseRevision,
    CaseSource,
)
from cases.source_policy import CaseSourcePolicyPacket

PRIMARY_REVISION_KEYS = ("research-2026", "default", "v1")


def pick_primary_revision(revisions: list[CaseRevision]) -> Optional[CaseRevision]:
    if not revisions:
        return None
    by_key = {r.revision_key: r for r in revisions}
    for key in PRIMARY_REVISION_KEYS:
        if key in by_key:
            return by_key[key]
    return sorted(revisions, key=lambda r: r.id or 0)[0]


def list_catalog_query(
    db: Session,
    *,
    manufacturer: Optional[str] = None,
    format_family: Optional[str] = None,
    production_status: Optional[str] = None,
    powered: Optional[bool] = None,
    q: Optional[str] = None,
    capacity_unit: Optional[str] = None,
    min_capacity: Optional[float] = None,
    max_capacity: Optional[float] = None,
    min_rows: Optional[int] = None,
    max_rows: Optional[int] = None,
    min_depth_mm: Optional[float] = None,
    min_pos12_ma: Optional[int] = None,
    min_neg12_ma: Optional[int] = None,
    min_pos5_ma: Optional[int] = None,
    portable: Optional[bool] = None,
    removable_lid: Optional[bool] = None,
    integrated_stand: Optional[bool] = None,
    feature_key: Optional[str] = None,
) -> Any:
    """Build a filtered CaseCatalog query, joining revision/power when needed."""

    needs_revision = any(
        v is not None
        for v in (
            capacity_unit,
            min_capacity,
            max_capacity,
            min_rows,
            max_rows,
            min_depth_mm,
            portable,
            removable_lid,
            integrated_stand,
        )
    )
    needs_power = any(v is not None for v in (min_pos12_ma, min_neg12_ma, min_pos5_ma))
    needs_feature = feature_key is not None

    query = db.query(CaseCatalog)

    if needs_revision or needs_power or needs_feature:
        query = query.join(CaseRevision, CaseRevision.case_id == CaseCatalog.id)

    if needs_power:
        query = query.outerjoin(CasePowerSystem, CasePowerSystem.revision_id == CaseRevision.id)

    if needs_feature:
        assert feature_key is not None
        query = query.join(CaseFeature, CaseFeature.revision_id == CaseRevision.id).filter(
            CaseFeature.feature_key == feature_key
        )

    if manufacturer:
        query = query.filter(CaseCatalog.manufacturer.ilike(f"%{manufacturer}%"))
    if format_family:
        query = query.filter(CaseCatalog.format_family == format_family)
    if production_status:
        query = query.filter(CaseCatalog.production_status == production_status)
    if powered is not None:
        query = query.filter(CaseCatalog.powered.is_(bool(powered)))
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                CaseCatalog.manufacturer.ilike(like),
                CaseCatalog.model.ilike(like),
                CaseCatalog.slug.ilike(like),
            )
        )

    if capacity_unit:
        query = query.filter(CaseRevision.capacity_unit == capacity_unit)
    if min_capacity is not None:
        query = query.filter(CaseRevision.capacity_value >= min_capacity)
    if max_capacity is not None:
        query = query.filter(CaseRevision.capacity_value <= max_capacity)
    if min_rows is not None:
        query = query.filter(CaseRevision.row_count >= min_rows)
    if max_rows is not None:
        query = query.filter(CaseRevision.row_count <= max_rows)
    if min_depth_mm is not None:
        # Prefer explicit usable/min depth; fall back to max when only max is known.
        query = query.filter(
            or_(
                CaseRevision.depth_min_mm >= min_depth_mm,
                CaseRevision.depth_max_mm >= min_depth_mm,
            )
        )
    if portable is not None:
        query = query.filter(CaseRevision.portable.is_(bool(portable)))
    if removable_lid is not None:
        query = query.filter(CaseRevision.removable_lid.is_(bool(removable_lid)))
    if integrated_stand is not None:
        query = query.filter(CaseRevision.integrated_stand.is_(bool(integrated_stand)))

    if min_pos12_ma is not None:
        query = query.filter(CasePowerSystem.current_pos12_ma >= min_pos12_ma)
    if min_neg12_ma is not None:
        query = query.filter(CasePowerSystem.current_neg12_ma >= min_neg12_ma)
    if min_pos5_ma is not None:
        query = query.filter(CasePowerSystem.current_pos5_ma >= min_pos5_ma)

    return query.distinct()


def get_case_by_slug(db: Session, slug: str) -> Optional[CaseCatalog]:
    return (
        db.query(CaseCatalog)
        .options(
            selectinload(CaseCatalog.revisions).selectinload(CaseRevision.rows),
            selectinload(CaseCatalog.revisions).selectinload(CaseRevision.power_systems),
            selectinload(CaseCatalog.revisions).selectinload(CaseRevision.features),
            selectinload(CaseCatalog.prices),
            selectinload(CaseCatalog.sources),
        )
        .filter(CaseCatalog.slug == slug)
        .first()
    )


def policy_by_source_ids(db: Session, source_ids: list[int]) -> dict[int, CaseSourcePolicyPacket]:
    if not source_ids:
        return {}
    rows = (
        db.query(CaseSourcePolicyPacket)
        .filter(CaseSourcePolicyPacket.source_id.in_(source_ids))
        .all()
    )
    return {row.source_id: row for row in rows}


def manufacturer_counts(db: Session) -> list[tuple[str, int]]:
    return (
        db.query(CaseCatalog.manufacturer, func.count(CaseCatalog.id))
        .group_by(CaseCatalog.manufacturer)
        .order_by(CaseCatalog.manufacturer.asc())
        .all()
    )


def format_counts(db: Session) -> list[tuple[str, int]]:
    return (
        db.query(CaseCatalog.format_family, func.count(CaseCatalog.id))
        .group_by(CaseCatalog.format_family)
        .order_by(CaseCatalog.format_family.asc())
        .all()
    )


def catalog_stats(db: Session) -> dict[str, Any]:
    case_count = db.query(func.count(CaseCatalog.id)).scalar() or 0
    revision_count = db.query(func.count(CaseRevision.id)).scalar() or 0
    manufacturer_count = db.query(func.count(func.distinct(CaseCatalog.manufacturer))).scalar() or 0

    format_family_counts = {
        family: count for family, count in format_counts(db) if family is not None
    }
    production_status_counts = {
        status: count
        for status, count in (
            db.query(CaseCatalog.production_status, func.count(CaseCatalog.id))
            .group_by(CaseCatalog.production_status)
            .all()
        )
        if status is not None
    }

    powered_true = (
        db.query(func.count(CaseCatalog.id)).filter(CaseCatalog.powered.is_(True)).scalar() or 0
    )
    powered_false = (
        db.query(func.count(CaseCatalog.id)).filter(CaseCatalog.powered.is_(False)).scalar() or 0
    )
    powered_null = (
        db.query(func.count(CaseCatalog.id)).filter(CaseCatalog.powered.is_(None)).scalar() or 0
    )

    capacity_unit_counts = {
        unit: count
        for unit, count in (
            db.query(CaseRevision.capacity_unit, func.count(CaseRevision.id))
            .group_by(CaseRevision.capacity_unit)
            .all()
        )
        if unit is not None
    }

    with_power_rails = (
        db.query(func.count(func.distinct(CasePowerSystem.revision_id)))
        .filter(
            or_(
                CasePowerSystem.current_pos12_ma.isnot(None),
                CasePowerSystem.current_neg12_ma.isnot(None),
                CasePowerSystem.current_pos5_ma.isnot(None),
            )
        )
        .scalar()
        or 0
    )
    with_depth = (
        db.query(func.count(CaseRevision.id))
        .filter(
            or_(
                CaseRevision.depth_min_mm.isnot(None),
                CaseRevision.depth_max_mm.isnot(None),
            )
        )
        .scalar()
        or 0
    )
    with_prices = db.query(func.count(func.distinct(CasePrice.case_id))).scalar() or 0
    with_sources = db.query(func.count(func.distinct(CaseSource.case_id))).scalar() or 0
    source_packet_count = db.query(func.count(CaseSourcePolicyPacket.id)).scalar() or 0

    return {
        "case_count": int(case_count),
        "revision_count": int(revision_count),
        "manufacturer_count": int(manufacturer_count),
        "format_family_counts": format_family_counts,
        "production_status_counts": production_status_counts,
        "powered_counts": {
            "true": int(powered_true),
            "false": int(powered_false),
            "null": int(powered_null),
        },
        "capacity_unit_counts": capacity_unit_counts,
        "with_power_rails": int(with_power_rails),
        "with_depth": int(with_depth),
        "with_prices": int(with_prices),
        "with_sources": int(with_sources),
        "source_packet_count": int(source_packet_count),
    }
