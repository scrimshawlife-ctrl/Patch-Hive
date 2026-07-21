"""BrandSurfacePolicy — Zero State understated; PatchHive Cyber Hive hero."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from export.patchbook.design.layout_ir import BrandMarkRef, PatchPageLayoutIR

FORBIDDEN_STRINGS = (
    "AAL product",
    "Applied Alchemy Labs product",
    "an AAL product",
)

# Cyber Hive accent (design tokens)
CYBER_HIVE_AMBER = "#F5A623"
CYBER_HIVE_GRAPHITE = "#1A1A1A"
CYBER_HIVE_CYAN = "#00D4C8"
ZERO_STATE_MUTED = "#6B7280"


@dataclass(frozen=True)
class BrandSurfaceRule:
    page_roles: tuple[str, ...]
    max_bbox_ratio: float
    max_opacity: float
    max_mark_height_pt: float
    mark_ids: tuple[str, ...]


ZERO_STATE_RULES: tuple[BrandSurfaceRule, ...] = (
    BrandSurfaceRule(
        page_roles=("cover", "title_signature", "colophon", "back_cover", "copyright"),
        max_bbox_ratio=0.08,
        max_opacity=0.85,
        max_mark_height_pt=18.0,
        mark_ids=("zero_state",),
    ),
    BrandSurfaceRule(
        page_roles=("footer",),
        max_bbox_ratio=0.02,
        max_opacity=0.55,
        max_mark_height_pt=8.0,
        mark_ids=("zero_state",),
    ),
    BrandSurfaceRule(
        page_roles=("pdf_metadata",),
        max_bbox_ratio=1.0,
        max_opacity=1.0,
        max_mark_height_pt=100.0,
        mark_ids=("zero_state", "patchhive"),
    ),
)

PATCHHIVE_HERO_RULES: tuple[BrandSurfaceRule, ...] = (
    BrandSurfaceRule(
        page_roles=("cover", "title_signature"),
        max_bbox_ratio=0.12,
        max_opacity=1.0,
        max_mark_height_pt=48.0,
        mark_ids=("patchhive",),
    ),
)

PDF_CREATOR_PATTERN = "PatchHive PatchBook; A Zero State Product"


@dataclass(frozen=True)
class BrandPolicyResult:
    ok: bool
    violations: tuple[str, ...]


def scan_forbidden_strings(texts: Iterable[str]) -> BrandPolicyResult:
    violations: list[str] = []
    for text in texts:
        lower = text.lower()
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden.lower() in lower:
                violations.append(f"forbidden_string:{forbidden}")
    return BrandPolicyResult(ok=not violations, violations=tuple(violations))


def validate_brand_marks(
    pages: Iterable[PatchPageLayoutIR],
    *,
    page_area_pt: float = 612.0 * 792.0,
) -> BrandPolicyResult:
    violations: list[str] = []
    for page in pages:
        for mark in page.brand_marks:
            if mark.mark_id == "zero_state":
                if not _mark_allowed(mark, ZERO_STATE_RULES, page_area_pt):
                    violations.append(f"zero_state_mark_policy:{page.page_id}:{mark.page_role}")
            elif mark.mark_id == "patchhive":
                # PatchHive allowed more freely; only flag if absurdly large on footer
                if mark.page_role == "footer":
                    _, _, _, h = mark.bbox_pt
                    if h > 14:
                        violations.append(f"patchhive_footer_oversized:{page.page_id}")
        # Text scan
        for run in page.text_runs:
            scan = scan_forbidden_strings([run.text])
            if not scan.ok:
                violations.extend(scan.violations)
    return BrandPolicyResult(ok=not violations, violations=tuple(violations))


def _mark_allowed(
    mark: BrandMarkRef, rules: tuple[BrandSurfaceRule, ...], page_area: float
) -> bool:
    _, _, w, h = mark.bbox_pt
    area_ratio = (w * h) / page_area if page_area else 0
    for rule in rules:
        if mark.page_role not in rule.page_roles:
            continue
        if mark.mark_id not in rule.mark_ids:
            continue
        if area_ratio > rule.max_bbox_ratio:
            return False
        if mark.opacity > rule.max_opacity:
            return False
        if h > rule.max_mark_height_pt:
            return False
        return True
    # zero_state on body execution without rule → fail
    return False
