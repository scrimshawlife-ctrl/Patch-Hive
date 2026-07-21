"""Unit tests for PatchBook Design Engine style recipe + layout IR contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from export.patchbook.design import (
    ARTISTIC_MODES,
    DESIGN_ENGINE_VERSION,
    LAYOUT_IR_SCHEMA_VERSION,
    STYLE_RECIPE_SCHEMA_VERSION,
    LayoutRegion,
    OutputProfile,
    PageKind,
    PatchBookMode,
    PatchPageLayoutIR,
    RequestStyleRecipe,
    ResolvedStyleRecipe,
    StyleConstraints,
    StyleWeights,
    TemplateFamilyId,
    TextRun,
    composition_hash,
    default_request_recipe,
    influence_ids,
    recipe_hash,
)
from export.patchbook.design.layout_ir import BrandMarkRef
from export.patchbook.design.recipe import BookProfile, ConstraintResolutionEvent


def test_default_request_recipe_professional_signal_manual() -> None:
    recipe = default_request_recipe(seed=384290)
    assert recipe.schema_version == STYLE_RECIPE_SCHEMA_VERSION
    assert recipe.engine_version == DESIGN_ENGINE_VERSION
    assert recipe.mode == PatchBookMode.PROFESSIONAL
    assert recipe.template_family == TemplateFamilyId.SIGNAL_MANUAL
    assert recipe.weights.legibility == 90
    assert recipe.weights.surrealism == 0
    assert recipe.seed == 384290
    assert "engineering" in recipe.influences


def test_recipe_hash_deterministic() -> None:
    a = default_request_recipe(seed=1)
    b = default_request_recipe(seed=1)
    c = default_request_recipe(seed=2)
    assert recipe_hash(a) == recipe_hash(b)
    assert recipe_hash(a) != recipe_hash(c)
    assert len(recipe_hash(a)) == 64


def test_artistic_mode_requires_disclosure_and_appendix() -> None:
    with pytest.raises(ValidationError, match="artistic_disclosure"):
        RequestStyleRecipe(
            mode=PatchBookMode.GALLERY,
            template_family=TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
            constraints=StyleConstraints(canonical_appendix_required=True),
        )
    with pytest.raises(ValidationError, match="canonical_appendix"):
        RequestStyleRecipe(
            mode=PatchBookMode.SURREAL,
            constraints=StyleConstraints(artistic_disclosure_acknowledged=True),
        )
    ok = RequestStyleRecipe(
        mode=PatchBookMode.SYMBOLIC,
        template_family=TemplateFamilyId.RITUAL_MACHINE,
        constraints=StyleConstraints(
            artistic_disclosure_acknowledged=True,
            canonical_appendix_required=True,
            book_profile=BookProfile.PUBLICATION,
        ),
    )
    assert ok.mode in ARTISTIC_MODES


def test_unknown_influence_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown influence"):
        RequestStyleRecipe(influences={"not_a_real_influence": 50})


def test_influence_catalog_has_expected_count() -> None:
    ids = influence_ids()
    assert len(ids) == 32
    assert "cyber_hive" in ids
    assert "open_form_zero_state" in ids


def test_resolved_recipe_frozen_and_zs_cap() -> None:
    base = default_request_recipe()
    resolved = ResolvedStyleRecipe(
        mode=base.mode,
        template_family=base.template_family,
        template_family_version=base.template_family_version,
        seed=base.seed,
        weights=base.weights,
        influences=base.influences,
        constraints=base.constraints,
        output_profile=base.output_profile,
        events=(
            ConstraintResolutionEvent(
                code="CLAMP_SURREALISM",
                severity="info",
                message="Professional mode reduced surrealism on technical pages",
                field="weights.surrealism",
                requested=80,
                resolved=0,
                authority_layer=5,
            ),
        ),
        resolved_tier="core",
        zero_state_brand_cap=10,
    )
    assert resolved.events[0].code == "CLAMP_SURREALISM"
    with pytest.raises(ValidationError):
        resolved.seed = 99  # type: ignore[misc]  # frozen

    with pytest.raises(ValidationError, match="zero_state_brand_cap"):
        ResolvedStyleRecipe(
            mode=base.mode,
            template_family=base.template_family,
            template_family_version="1.0.0",
            seed=0,
            weights=StyleWeights(brand_presence=5),
            constraints=StyleConstraints(),
            output_profile=OutputProfile.PRINT_PDF,
            zero_state_brand_cap=20,
        )


def test_layout_ir_execution_requires_patch_id() -> None:
    region = LayoutRegion(
        region_id="identity",
        role="identity",
        required=True,
        bbox_pt=(36.0, 700.0, 540.0, 48.0),
        reading_order=0,
    )
    with pytest.raises(ValidationError, match="patch_artifact_id"):
        PatchPageLayoutIR(
            page_id="p1",
            page_index=0,
            page_kind=PageKind.EXECUTION,
            page_size="us_letter",
            regions=(region,),
            reading_order=("identity",),
        )

    page = PatchPageLayoutIR(
        page_id="p1",
        page_index=0,
        page_kind=PageKind.EXECUTION,
        patch_artifact_id="patch:1",
        page_size="us_letter",
        regions=(region,),
        text_runs=(
            TextRun(
                run_id="t1",
                region_id="identity",
                text="Test Patch",
                style_role="display",
                font_size_pt=16.0,
            ),
        ),
        reading_order=("identity",),
        layout_algorithm_id="orthogonal_schematic",
        brand_marks=(
            BrandMarkRef(
                mark_id="zero_state",
                page_role="footer",
                bbox_pt=(36.0, 24.0, 80.0, 8.0),
                opacity=0.5,
            ),
        ),
    )
    assert page.schema_version == LAYOUT_IR_SCHEMA_VERSION
    assert page.diagram_literal is True


def test_composition_hash_stable_and_order_independent() -> None:
    region = LayoutRegion(
        region_id="diagram",
        role="diagram",
        required=True,
        bbox_pt=(36.0, 200.0, 540.0, 400.0),
        reading_order=0,
    )
    p0 = PatchPageLayoutIR(
        page_id="p0",
        page_index=0,
        page_kind=PageKind.FRONT_MATTER,
        page_size="us_letter",
        regions=(region,),
        reading_order=("diagram",),
    )
    p1 = PatchPageLayoutIR(
        page_id="p1",
        page_index=1,
        page_kind=PageKind.EXECUTION,
        patch_artifact_id="patch:a",
        page_size="us_letter",
        regions=(region,),
        reading_order=("diagram",),
    )
    h1 = composition_hash(
        library_content_hash="lib1",
        bridge_artifact_manifest_hash="bridge1",
        resolved_recipe_hash="recipe1",
        layout_irs=[p0, p1],
        design_engine_version=DESIGN_ENGINE_VERSION,
    )
    h2 = composition_hash(
        library_content_hash="lib1",
        bridge_artifact_manifest_hash="bridge1",
        resolved_recipe_hash="recipe1",
        layout_irs=[p1, p0],  # reverse input order
        design_engine_version=DESIGN_ENGINE_VERSION,
    )
    assert h1 == h2
    assert len(h1) == 64

    h3 = composition_hash(
        library_content_hash="lib2",
        bridge_artifact_manifest_hash="bridge1",
        resolved_recipe_hash="recipe1",
        layout_irs=[p0, p1],
        design_engine_version=DESIGN_ENGINE_VERSION,
    )
    assert h1 != h3


def test_professional_may_request_high_experimental_type_without_hard_fail() -> None:
    """Request may be out of range; resolver soft-clamps (KD-16)."""
    recipe = RequestStyleRecipe(
        mode=PatchBookMode.PROFESSIONAL,
        weights=StyleWeights(experimental_typography=80),
    )
    assert recipe.weights.experimental_typography == 80
