"""Accessibility validation for Design Engine compositions."""

from __future__ import annotations

from dataclasses import dataclass

from export.patchbook.design.layout_ir import PageKind, PatchPageLayoutIR
from export.patchbook.design.recipe import ResolvedStyleRecipe

MIN_BODY_PT_PRINT = 9.5
MIN_CONTRAST = 4.5


@dataclass(frozen=True)
class A11yIssue:
    code: str
    severity: str
    message: str
    page_id: str | None = None


@dataclass(frozen=True)
class A11yReport:
    ok: bool
    issues: tuple[A11yIssue, ...]


def validate_composition_a11y(
    pages: list[PatchPageLayoutIR] | tuple[PatchPageLayoutIR, ...],
    recipe: ResolvedStyleRecipe,
) -> A11yReport:
    issues: list[A11yIssue] = []
    min_body = recipe.constraints.minimum_body_size_pt
    if min_body < MIN_BODY_PT_PRINT and recipe.output_profile.value.startswith("print"):
        issues.append(
            A11yIssue(
                code="FONT_BELOW_MINIMUM",
                severity="error",
                message=f"minimum_body_size_pt {min_body} < {MIN_BODY_PT_PRINT}",
            )
        )

    if recipe.constraints.minimum_contrast_ratio < MIN_CONTRAST:
        issues.append(
            A11yIssue(
                code="CONTRAST_BELOW_AA",
                severity="error",
                message=f"minimum_contrast_ratio {recipe.constraints.minimum_contrast_ratio} < {MIN_CONTRAST}",
            )
        )

    if not recipe.constraints.color_independent_diagrams:
        issues.append(
            A11yIssue(
                code="COLOR_ONLY_DIAGRAMS",
                severity="error",
                message="color_independent_diagrams must be true for production export",
            )
        )

    for page in pages:
        if page.page_kind in (PageKind.EXECUTION, PageKind.APPENDIX_EXECUTION):
            roles = {r.role for r in page.regions}
            if "footer" not in roles:
                issues.append(
                    A11yIssue(
                        code="EXECUTION_FOOTER_MISSING",
                        severity="error",
                        message="execution pages require footer band",
                        page_id=page.page_id,
                    )
                )
            if "diagram" not in roles and page.diagram_literal:
                # non-literal plates may omit; literal execution needs diagram region
                issues.append(
                    A11yIssue(
                        code="DIAGRAM_REGION_MISSING",
                        severity="warning",
                        message="literal execution page missing diagram region",
                        page_id=page.page_id,
                    )
                )
            if not page.reading_order:
                issues.append(
                    A11yIssue(
                        code="READING_ORDER_EMPTY",
                        severity="error",
                        message="reading_order required",
                        page_id=page.page_id,
                    )
                )
        for run in page.text_runs:
            if run.style_role in {"body", "warning"} and run.font_size_pt < min_body:
                issues.append(
                    A11yIssue(
                        code="TEXT_RUN_BELOW_MINIMUM",
                        severity="error",
                        message=f"run {run.run_id} font_size_pt {run.font_size_pt} < {min_body}",
                        page_id=page.page_id,
                    )
                )

    blocking = [i for i in issues if i.severity == "error"]
    return A11yReport(ok=not blocking, issues=tuple(issues))
