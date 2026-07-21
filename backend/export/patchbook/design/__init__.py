"""PatchBook Design Engine contracts (presentation layer only).

Layer A (canonical patch content) is never mutated here. See
``docs/design/PATCHBOOK_DESIGN_ENGINE.md``.
"""

from __future__ import annotations

from .layout_ir import (
    LAYOUT_IR_SCHEMA_VERSION,
    LayoutRegion,
    PageKind,
    PatchPageLayoutIR,
    TextRun,
    composition_hash,
)
from .constraints import resolve_style_recipe
from .recipe import (
    ARTISTIC_MODES,
    DESIGN_ENGINE_VERSION,
    STYLE_RECIPE_SCHEMA_VERSION,
    ConstraintResolutionEvent,
    OutputProfile,
    PatchBookMode,
    RequestStyleRecipe,
    ResolvedStyleRecipe,
    StyleConstraints,
    StyleWeights,
    TemplateFamilyId,
    default_request_recipe,
    influence_ids,
    recipe_hash,
)

__all__ = [
    "ARTISTIC_MODES",
    "DESIGN_ENGINE_VERSION",
    "LAYOUT_IR_SCHEMA_VERSION",
    "STYLE_RECIPE_SCHEMA_VERSION",
    "ConstraintResolutionEvent",
    "LayoutRegion",
    "OutputProfile",
    "PageKind",
    "PatchBookMode",
    "PatchPageLayoutIR",
    "RequestStyleRecipe",
    "ResolvedStyleRecipe",
    "StyleConstraints",
    "StyleWeights",
    "TemplateFamilyId",
    "TextRun",
    "composition_hash",
    "default_request_recipe",
    "influence_ids",
    "recipe_hash",
    "resolve_style_recipe",
]
