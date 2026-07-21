"""Print / pack preflight gates for Design Engine exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from export.patchbook.design.a11y import A11yReport, validate_composition_a11y
from export.patchbook.design.brand_policy import BrandPolicyResult, validate_brand_marks
from export.patchbook.design.layout_ir import PatchPageLayoutIR
from export.patchbook.design.recipe import ResolvedStyleRecipe

MAX_MEAN_INK_COVERAGE = 0.92  # heuristic budget; full ink analysis later


@dataclass(frozen=True)
class PreflightIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class PreflightReport:
    ok: bool
    issues: tuple[PreflightIssue, ...]
    a11y: A11yReport
    brand: BrandPolicyResult


def run_preflight(
    pages: list[PatchPageLayoutIR] | tuple[PatchPageLayoutIR, ...],
    recipe: ResolvedStyleRecipe,
    *,
    pack_dir: Path | None = None,
) -> PreflightReport:
    issues: list[PreflightIssue] = []
    a11y = validate_composition_a11y(pages, recipe)
    for item in a11y.issues:
        issues.append(PreflightIssue(code=item.code, severity=item.severity, message=item.message))

    brand = validate_brand_marks(pages)
    if not brand.ok:
        for v in brand.violations:
            issues.append(PreflightIssue(code="BRAND_POLICY", severity="error", message=v))

    # Region density heuristic as stand-in for ink coverage
    for page in pages:
        area = 0.0
        for region in page.regions:
            _, _, w, h = region.bbox_pt
            area += w * h
        page_area = 612.0 * 792.0
        coverage = area / page_area if page_area else 0.0
        if coverage > MAX_MEAN_INK_COVERAGE:
            issues.append(
                PreflightIssue(
                    code="INK_COVERAGE_HIGH",
                    severity="warning",
                    message=f"page {page.page_id} region coverage {coverage:.2f} > {MAX_MEAN_INK_COVERAGE}",
                )
            )

    if pack_dir is not None:
        required = [
            pack_dir / "PatchBook.pdf",
            pack_dir / "manifest" / "patch-book.json",
            pack_dir / "technical" / "companion.txt",
        ]
        for path in required:
            if not path.exists():
                issues.append(
                    PreflightIssue(
                        code="PACK_FILE_MISSING",
                        severity="error",
                        message=f"missing {path.relative_to(pack_dir)}",
                    )
                )
        if recipe.constraints.canonical_appendix_required:
            appendix = pack_dir / "technical" / "PatchBook-execution.pdf"
            if not appendix.exists():
                issues.append(
                    PreflightIssue(
                        code="APPENDIX_MISSING",
                        severity="error",
                        message="artistic/appendix mode requires technical/PatchBook-execution.pdf",
                    )
                )

    blocking = [i for i in issues if i.severity == "error"]
    return PreflightReport(
        ok=not blocking and a11y.ok and brand.ok,
        issues=tuple(issues),
        a11y=a11y,
        brand=brand,
    )
