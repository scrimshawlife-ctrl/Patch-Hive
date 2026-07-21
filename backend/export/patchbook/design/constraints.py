"""Constraint resolver: RequestStyleRecipe → ResolvedStyleRecipe (KD-7, KD-16)."""

from __future__ import annotations

from typing import Literal

from export.patchbook.design.influences import apply_influence_transfers, normalize_influences
from export.patchbook.design.presets import MODE_WEIGHT_DEFAULTS
from export.patchbook.design.recipe import (
    ARTISTIC_MODES,
    DESIGN_ENGINE_VERSION,
    BookProfile,
    ConstraintResolutionEvent,
    PatchBookMode,
    RequestStyleRecipe,
    ResolvedStyleRecipe,
    TemplateFamilyId,
    recipe_hash,
)

TierName = Literal["free", "core", "pro", "studio"]


class StyleResolveError(ValueError):
    """Hard-fail before debit (disclosure, unknown family after tier, etc.)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def resolve_style_recipe(
    request: RequestStyleRecipe,
    *,
    resolved_tier: TierName = "core",
    family_allowed: bool = True,
    publication_enabled: bool = False,
    engine_version: str = DESIGN_ENGINE_VERSION,
) -> ResolvedStyleRecipe:
    """Resolve on API thread before debit. Worker re-validates sealed result only."""

    events: list[ConstraintResolutionEvent] = []
    weights = request.weights.model_copy(deep=True)
    constraints = request.constraints.model_copy(deep=True)
    family = request.template_family
    mode = request.mode

    # Rank 4 — explicit mode: artistic forces appendix + disclosure already on request;
    # force dual-artifact book profile.
    if mode in ARTISTIC_MODES:
        if not constraints.artistic_disclosure_acknowledged:
            raise StyleResolveError(
                "ARTISTIC_DISCLOSURE_REQUIRED",
                "Artistic modes require disclosure acknowledgement",
            )
        if not constraints.canonical_appendix_required:
            constraints = constraints.model_copy(update={"canonical_appendix_required": True})
            events.append(
                ConstraintResolutionEvent(
                    code="FORCE_TECHNICAL_APPENDIX",
                    severity="info",
                    message="Artistic mode requires a canonical technical appendix",
                    field="constraints.canonical_appendix_required",
                    requested=False,
                    resolved=True,
                    authority_layer=4,
                )
            )
        if constraints.book_profile == BookProfile.EXECUTION_PAGE:
            constraints = constraints.model_copy(update={"book_profile": BookProfile.PUBLICATION})
            events.append(
                ConstraintResolutionEvent(
                    code="FORCE_PUBLICATION_PROFILE",
                    severity="info",
                    message="Artistic mode forces dual-artifact publication profile",
                    field="constraints.book_profile",
                    requested="execution_page",
                    resolved="publication",
                    authority_layer=4,
                )
            )
        if not publication_enabled and constraints.book_profile == BookProfile.PUBLICATION:
            # Fail closed before debit when artistic/publication requires dual-artifact
            # but the product flag is off (unless tests force publication_enabled).
            raise StyleResolveError(
                "PUBLICATION_PROFILE_DISABLED",
                "Publication / artistic dual-artifact profile requires "
                "ENABLE_PATCHBOOK_PUBLICATION_PROFILE=true",
            )

    # Tier family gate (server authority)
    if not family_allowed:
        fallback = TemplateFamilyId.SIGNAL_MANUAL
        events.append(
            ConstraintResolutionEvent(
                code="FAMILY_TIER_DOWNGRADE",
                severity="warning",
                message=f"Family {family.value} unavailable at tier {resolved_tier}; using signal_manual",
                field="template_family",
                requested=family.value,
                resolved=fallback.value,
                authority_layer=4,
            )
        )
        family = fallback

    # Rank 5 — legibility target clamps experimental typography outside artistic
    if mode not in ARTISTIC_MODES and weights.experimental_typography > 40:
        events.append(
            ConstraintResolutionEvent(
                code="CLAMP_EXPERIMENTAL_TYPOGRAPHY",
                severity="info",
                message="Non-artistic mode clamps experimental_typography to ≤40",
                field="weights.experimental_typography",
                requested=weights.experimental_typography,
                resolved=40,
                authority_layer=5,
            )
        )
        weights = weights.model_copy(update={"experimental_typography": 40})

    # Professional mode soft floor on legibility / diagram literalness
    if mode == PatchBookMode.PROFESSIONAL:
        if weights.legibility < 85:
            events.append(
                ConstraintResolutionEvent(
                    code="CLAMP_LEGIBILITY_PROFESSIONAL",
                    severity="info",
                    message="Professional mode raises legibility floor to 85",
                    field="weights.legibility",
                    requested=weights.legibility,
                    resolved=85,
                    authority_layer=5,
                )
            )
            weights = weights.model_copy(update={"legibility": 85})
        if weights.surrealism > 20:
            events.append(
                ConstraintResolutionEvent(
                    code="CLAMP_SURREALISM",
                    severity="info",
                    message="Professional mode reduced surrealism on technical pages",
                    field="weights.surrealism",
                    requested=weights.surrealism,
                    resolved=10,
                    authority_layer=5,
                )
            )
            weights = weights.model_copy(update={"surrealism": 10})

    # Rank 8 — influence normalize (does not mutate Layer A; records pressure only)
    norm = normalize_influences(request.influences)
    eff = apply_influence_transfers(weights, norm.normalized)
    # Fold effective ornamentation/white_space back into sealed weights when clamped
    new_orn = int(round(eff.ornamentation_eff))
    if new_orn != weights.ornamentation:
        events.append(
            ConstraintResolutionEvent(
                code="INFLUENCE_ORNAMENTATION",
                severity="info",
                message="Influence mixer adjusted ornamentation",
                field="weights.ornamentation",
                requested=weights.ornamentation,
                resolved=_clamp_int(new_orn, 0, 100),
                authority_layer=8,
            )
        )
        weights = weights.model_copy(update={"ornamentation": _clamp_int(new_orn, 0, 100)})

    # Zero State brand cap ≤ 0.4 * brand_presence, max 12
    zs_cap = min(int(weights.brand_presence * 0.4), 12)

    # Blend with mode defaults lightly when user left sparse weights at engine default
    # (no silent mode overwrite of explicit user vector — only fill via events if needed)

    resolved = ResolvedStyleRecipe(
        schema_version=request.schema_version,
        engine_version=engine_version,
        mode=mode,
        template_family=family,
        template_family_version=request.template_family_version,
        seed=request.seed,
        weights=weights,
        influences=norm.raw,
        constraints=constraints,
        output_profile=request.output_profile,
        preset_id=request.preset_id,
        notes=request.notes,
        events=tuple(events),
        resolved_tier=resolved_tier,
        zero_state_brand_cap=zs_cap,
    )
    # Ensure hash is stable
    _ = recipe_hash(resolved)
    return resolved


def revalidate_resolved_recipe(
    sealed: ResolvedStyleRecipe,
    *,
    expected_hash: str,
    expected_engine_version: str,
) -> None:
    """Worker path: no re-resolve; fail closed on drift."""
    if sealed.engine_version != expected_engine_version:
        raise StyleResolveError(
            "DESIGN_RECIPE_RESOLVE_DRIFT",
            f"engine_version mismatch: sealed={sealed.engine_version} expected={expected_engine_version}",
        )
    actual = recipe_hash(sealed)
    if actual != expected_hash:
        raise StyleResolveError(
            "DESIGN_RECIPE_RESOLVE_DRIFT",
            "resolved style recipe hash mismatch",
        )


def professional_default_resolved(*, seed: int = 0, tier: TierName = "core") -> ResolvedStyleRecipe:
    """Server default when client omits style recipe (PR-05 vertical)."""
    from export.patchbook.design.recipe import default_request_recipe

    req = default_request_recipe(seed=seed)
    # Align weights toward professional mode table
    req = req.model_copy(
        update={
            "weights": MODE_WEIGHT_DEFAULTS[PatchBookMode.PROFESSIONAL],
            "mode": PatchBookMode.PROFESSIONAL,
        }
    )
    return resolve_style_recipe(req, resolved_tier=tier, family_allowed=True)
