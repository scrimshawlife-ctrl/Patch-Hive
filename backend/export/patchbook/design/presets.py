"""Mode defaults and named presets for the PatchBook Design Engine."""

from __future__ import annotations

from export.patchbook.design.recipe import (
    ARTISTIC_MODES,
    PatchBookMode,
    RequestStyleRecipe,
    StyleConstraints,
    StyleWeights,
    TemplateFamilyId,
    BookProfile,
    OutputProfile,
)

# Full mode weight tables (design §9 / §A.6)
MODE_WEIGHT_DEFAULTS: dict[PatchBookMode, StyleWeights] = {
    PatchBookMode.PROFESSIONAL: StyleWeights(
        legibility=95,
        technical_density=85,
        editorial_expression=40,
        symbolism=5,
        abstraction=0,
        surrealism=0,
        ornamentation=12,
        grid_rigidity=85,
        white_space=50,
        visual_motion=25,
        materiality=15,
        brand_presence=12,
        diagram_literalness=95,
        historical_influence=5,
        experimental_typography=0,
    ),
    PatchBookMode.EDITORIAL: StyleWeights(
        legibility=85,
        technical_density=65,
        editorial_expression=85,
        symbolism=15,
        abstraction=10,
        surrealism=0,
        ornamentation=30,
        grid_rigidity=65,
        white_space=70,
        visual_motion=40,
        materiality=35,
        brand_presence=18,
        diagram_literalness=80,
        historical_influence=15,
        experimental_typography=10,
    ),
    PatchBookMode.COLLECTOR: StyleWeights(
        legibility=80,
        technical_density=60,
        editorial_expression=90,
        symbolism=20,
        abstraction=15,
        surrealism=5,
        ornamentation=45,
        grid_rigidity=55,
        white_space=75,
        visual_motion=45,
        materiality=65,
        brand_presence=22,
        diagram_literalness=75,
        historical_influence=20,
        experimental_typography=15,
    ),
    PatchBookMode.EDUCATIONAL: StyleWeights(
        legibility=100,
        technical_density=70,
        editorial_expression=50,
        symbolism=5,
        abstraction=0,
        surrealism=0,
        ornamentation=10,
        grid_rigidity=80,
        white_space=60,
        visual_motion=30,
        materiality=15,
        brand_presence=12,
        diagram_literalness=95,
        historical_influence=5,
        experimental_typography=0,
    ),
    PatchBookMode.TECHNICAL_ARCHIVE: StyleWeights(
        legibility=100,
        technical_density=100,
        editorial_expression=20,
        symbolism=0,
        abstraction=0,
        surrealism=0,
        ornamentation=0,
        grid_rigidity=95,
        white_space=35,
        visual_motion=10,
        materiality=10,
        brand_presence=10,
        diagram_literalness=100,
        historical_influence=25,
        experimental_typography=0,
    ),
    PatchBookMode.SYMBOLIC: StyleWeights(
        legibility=55,
        technical_density=50,
        editorial_expression=70,
        symbolism=95,
        abstraction=55,
        surrealism=10,
        ornamentation=50,
        grid_rigidity=50,
        white_space=60,
        visual_motion=55,
        materiality=40,
        brand_presence=15,
        diagram_literalness=40,
        historical_influence=20,
        experimental_typography=25,
    ),
    PatchBookMode.ABSTRACT: StyleWeights(
        legibility=35,
        technical_density=40,
        editorial_expression=80,
        symbolism=60,
        abstraction=95,
        surrealism=30,
        ornamentation=40,
        grid_rigidity=40,
        white_space=70,
        visual_motion=70,
        materiality=50,
        brand_presence=12,
        diagram_literalness=20,
        experimental_typography=45,
        historical_influence=10,
    ),
    PatchBookMode.SURREAL: StyleWeights(
        legibility=25,
        technical_density=35,
        editorial_expression=90,
        symbolism=70,
        abstraction=80,
        surrealism=95,
        ornamentation=55,
        grid_rigidity=25,
        white_space=65,
        visual_motion=85,
        materiality=60,
        brand_presence=10,
        diagram_literalness=15,
        historical_influence=15,
        experimental_typography=50,
    ),
    PatchBookMode.GALLERY: StyleWeights(
        legibility=15,
        technical_density=30,
        editorial_expression=100,
        symbolism=75,
        abstraction=90,
        surrealism=60,
        ornamentation=70,
        grid_rigidity=20,
        white_space=80,
        visual_motion=75,
        materiality=85,
        brand_presence=20,
        diagram_literalness=10,
        historical_influence=25,
        experimental_typography=75,
    ),
}

MODE_DEFAULT_FAMILY: dict[PatchBookMode, TemplateFamilyId] = {
    PatchBookMode.PROFESSIONAL: TemplateFamilyId.SIGNAL_MANUAL,
    PatchBookMode.EDITORIAL: TemplateFamilyId.OPEN_STATE,
    PatchBookMode.COLLECTOR: TemplateFamilyId.MUSEUM_OF_SIGNAL,
    PatchBookMode.EDUCATIONAL: TemplateFamilyId.MODULAR_FIELD_NOTES,
    PatchBookMode.TECHNICAL_ARCHIVE: TemplateFamilyId.CIRCUIT_ARCHIVE,
    PatchBookMode.SYMBOLIC: TemplateFamilyId.RITUAL_MACHINE,
    PatchBookMode.ABSTRACT: TemplateFamilyId.PATCH_CARTOGRAPHY,
    PatchBookMode.SURREAL: TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
    PatchBookMode.GALLERY: TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
}


def mode_base_recipe(mode: PatchBookMode, *, seed: int = 0) -> RequestStyleRecipe:
    artistic = mode in ARTISTIC_MODES
    return RequestStyleRecipe(
        mode=mode,
        template_family=MODE_DEFAULT_FAMILY[mode],
        seed=seed,
        weights=MODE_WEIGHT_DEFAULTS[mode],
        influences=_default_influences(mode),
        constraints=StyleConstraints(
            book_profile=(
                BookProfile.PUBLICATION if artistic or mode == PatchBookMode.COLLECTOR else BookProfile.EXECUTION_PAGE
            ),
            canonical_appendix_required=artistic,
            artistic_disclosure_acknowledged=artistic,
        ),
        output_profile=OutputProfile.PRINT_PDF,
    )


def _default_influences(mode: PatchBookMode) -> dict[str, int]:
    if mode == PatchBookMode.PROFESSIONAL:
        return {"engineering": 92, "swiss": 65, "scientific": 55, "cyber_hive": 24}
    if mode == PatchBookMode.TECHNICAL_ARCHIVE:
        return {"archival": 95, "engineering": 90, "technical_manual": 85}
    if mode == PatchBookMode.EDUCATIONAL:
        return {"technical_manual": 80, "field_notebook": 70, "swiss": 50}
    if mode == PatchBookMode.COLLECTOR:
        return {"museum": 80, "record_packaging": 55, "luxury": 40, "cyber_hive": 30}
    if mode == PatchBookMode.EDITORIAL:
        return {"editorial": 85, "swiss": 55, "museum": 40}
    if mode == PatchBookMode.SYMBOLIC:
        return {"symbolic": 95, "ritual": 70, "cyber_hive": 40}
    if mode == PatchBookMode.ABSTRACT:
        return {"abstract": 95, "generative_geometry": 70, "minimal": 30}
    if mode == PatchBookMode.SURREAL:
        return {"surreal": 95, "abstract": 70, "organic": 40}
    if mode == PatchBookMode.GALLERY:
        return {"museum": 70, "abstract": 80, "luxury": 50, "generative_geometry": 60}
    return {"engineering": 50}
