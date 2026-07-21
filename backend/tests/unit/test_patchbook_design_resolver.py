"""Constraint resolver + influence mixer tests."""

from __future__ import annotations

import pytest

from export.patchbook.design.constraints import (
    resolve_style_recipe,
)
from export.patchbook.design.influences import normalize_influences
from export.patchbook.design.recipe import (
    PatchBookMode,
    RequestStyleRecipe,
    StyleConstraints,
    StyleWeights,
    TemplateFamilyId,
    BookProfile,
    recipe_hash,
)


def test_professional_clamps_experimental_typography() -> None:
    req = RequestStyleRecipe(
        mode=PatchBookMode.PROFESSIONAL,
        weights=StyleWeights(experimental_typography=80, surrealism=90),
    )
    resolved = resolve_style_recipe(req, resolved_tier="core", family_allowed=True)
    assert resolved.weights.experimental_typography == 40
    assert resolved.weights.surrealism == 10
    codes = {e.code for e in resolved.events}
    assert "CLAMP_EXPERIMENTAL_TYPOGRAPHY" in codes
    assert "CLAMP_SURREALISM" in codes


def test_artistic_forces_appendix_and_publication() -> None:
    req = RequestStyleRecipe(
        mode=PatchBookMode.GALLERY,
        template_family=TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
        constraints=StyleConstraints(
            artistic_disclosure_acknowledged=True,
            canonical_appendix_required=True,
            book_profile=BookProfile.EXECUTION_PAGE,
        ),
    )
    resolved = resolve_style_recipe(
        req, resolved_tier="studio", family_allowed=True, publication_enabled=True
    )
    assert resolved.constraints.book_profile == BookProfile.PUBLICATION
    assert resolved.constraints.canonical_appendix_required is True


def test_artistic_fails_when_publication_flag_off() -> None:
    from export.patchbook.design.constraints import StyleResolveError

    req = RequestStyleRecipe(
        mode=PatchBookMode.SYMBOLIC,
        template_family=TemplateFamilyId.RITUAL_MACHINE,
        constraints=StyleConstraints(
            artistic_disclosure_acknowledged=True,
            canonical_appendix_required=True,
            book_profile=BookProfile.PUBLICATION,
        ),
    )
    with pytest.raises(StyleResolveError) as exc:
        resolve_style_recipe(req, resolved_tier="studio", publication_enabled=False)
    assert exc.value.code == "PUBLICATION_PROFILE_DISABLED"


def test_family_tier_downgrade() -> None:
    req = RequestStyleRecipe(
        mode=PatchBookMode.PROFESSIONAL,
        template_family=TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
    )
    resolved = resolve_style_recipe(req, resolved_tier="core", family_allowed=False)
    assert resolved.template_family == TemplateFamilyId.SIGNAL_MANUAL
    assert any(e.code == "FAMILY_TIER_DOWNGRADE" for e in resolved.events)


def test_influence_group_normalize_deterministic() -> None:
    raw = {"engineering": 80, "scientific": 80, "technical_manual": 80}
    a = normalize_influences(raw)
    b = normalize_influences(raw)
    assert a.normalized == b.normalized
    assert a.group_sums["g_density"] == 240
    # After normalize each is scaled so sum of scaled weights == 100 within group
    assert abs(sum(a.normalized[k] for k in raw) - 1.0) < 1e-6


def test_resolve_hash_stable() -> None:
    req = RequestStyleRecipe(seed=42)
    r1 = resolve_style_recipe(req, resolved_tier="core")
    r2 = resolve_style_recipe(req, resolved_tier="core")
    assert recipe_hash(r1) == recipe_hash(r2)


def test_artistic_without_disclosure_hard_fails_on_request() -> None:
    with pytest.raises(Exception):
        RequestStyleRecipe(mode=PatchBookMode.SURREAL)
