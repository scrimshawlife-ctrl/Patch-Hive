"""Template family specs — structurally unique (not palette swaps)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from export.patchbook.design.recipe import TemplateFamilyId

STRUCT_MIN_DISTANCE = 0.35

LayoutClass = Literal["diagram_first", "instruction_first", "performance_first"]
TierFloor = Literal["free", "core", "pro", "studio"]


@dataclass(frozen=True)
class StructuralFingerprint:
    layout_algorithm_id: str
    grid_modules: tuple[int, float, float]  # columns, baseline_pt, margin_ratio
    region_graph: tuple[str, ...]  # ordered region roles
    type_role_set: tuple[str, ...]
    diagram_encoding: tuple[str, ...]  # must include non-color cues
    default_page_kinds: tuple[str, ...]
    rhythm_signature: str

    def as_dict(self) -> dict[str, object]:
        return {
            "layout_algorithm_id": self.layout_algorithm_id,
            "grid_modules": list(self.grid_modules),
            "region_graph": list(self.region_graph),
            "type_role_set": list(self.type_role_set),
            "diagram_encoding": list(self.diagram_encoding),
            "default_page_kinds": list(self.default_page_kinds),
            "rhythm_signature": self.rhythm_signature,
        }


@dataclass(frozen=True)
class FamilySpec:
    family_id: TemplateFamilyId
    display_name: str
    layout_algorithm_id: str
    tier_floor: TierFloor
    default_layout_class: LayoutClass
    fingerprint: StructuralFingerprint
    cover_subtitle: str
    body_font: str
    mono_font: str
    accent_hex: str
    paper_bias: Literal["white", "warm", "dark", "vellum"]
    show_title_block: bool = False
    show_checklist: bool = False
    patent_disclaimer: bool = False
    require_full_cover_title: bool = True


def _fp(
    algorithm: str,
    *,
    cols: int,
    baseline: float,
    margin: float,
    regions: tuple[str, ...],
    types: tuple[str, ...],
    encoding: tuple[str, ...],
    kinds: tuple[str, ...],
    rhythm: str,
) -> StructuralFingerprint:
    return StructuralFingerprint(
        layout_algorithm_id=algorithm,
        grid_modules=(cols, baseline, margin),
        region_graph=regions,
        type_role_set=types,
        diagram_encoding=encoding,
        default_page_kinds=kinds,
        rhythm_signature=rhythm,
    )


_REGIONS_DIAGRAM = ("identity", "diagram", "intent", "construction", "operation", "footer")
_REGIONS_INSTRUCTION = ("identity", "construction", "diagram", "operation", "footer")
_REGIONS_PERF = ("identity", "operation", "diagram", "construction", "footer")
_REGIONS_PLATE = ("identity", "plate", "caption", "footer")
_TYPES_STANDARD = ("display", "body", "mono", "caption", "footer")
_TYPES_SERIF = ("display", "body", "mono", "caption", "footer", "serif")
_ENC = ("color", "dash", "number", "label")

FAMILIES: dict[TemplateFamilyId, FamilySpec] = {
    TemplateFamilyId.SIGNAL_MANUAL: FamilySpec(
        family_id=TemplateFamilyId.SIGNAL_MANUAL,
        display_name="Signal Manual",
        layout_algorithm_id="orthogonal_schematic",
        tier_floor="free",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "orthogonal_schematic",
            cols=12,
            baseline=8.0,
            margin=0.06,
            regions=_REGIONS_DIAGRAM,
            types=_TYPES_STANDARD,
            encoding=_ENC,
            kinds=("execution",),
            rhythm="diagram_first_55_25_20",
        ),
        cover_subtitle="Signal Manual · Engineering",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#F5A623",
        paper_bias="white",
    ),
    TemplateFamilyId.HIVE_SYSTEMS_ATLAS: FamilySpec(
        family_id=TemplateFamilyId.HIVE_SYSTEMS_ATLAS,
        display_name="Hive Systems Atlas",
        layout_algorithm_id="hex_cell_map",
        tier_floor="core",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "hex_cell_map",
            cols=10,
            baseline=7.0,
            margin=0.05,
            regions=("identity", "hex_map", "legend", "construction", "footer"),
            types=_TYPES_STANDARD,
            encoding=("color", "dash", "number", "label", "hex_cell"),
            kinds=("execution",),
            rhythm="atlas_hex_topology",
        ),
        cover_subtitle="Hive Systems Atlas · Topology",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#F5A623",
        paper_bias="dark",
    ),
    TemplateFamilyId.OPEN_STATE: FamilySpec(
        family_id=TemplateFamilyId.OPEN_STATE,
        display_name="Open State",
        layout_algorithm_id="open_asymmetric_sparse",
        tier_floor="core",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "open_asymmetric_sparse",
            cols=6,
            baseline=10.0,
            margin=0.12,
            regions=("identity", "diagram", "whitespace", "construction", "footer"),
            types=("display", "body", "mono", "caption", "footer", "light"),
            encoding=_ENC,
            kinds=("execution",),
            rhythm="sparse_asymmetric_open",
        ),
        cover_subtitle="Open State · Zero State geometry",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#3DDCFF",
        paper_bias="dark",
    ),
    TemplateFamilyId.MODULAR_FIELD_NOTES: FamilySpec(
        family_id=TemplateFamilyId.MODULAR_FIELD_NOTES,
        display_name="Modular Field Notes",
        layout_algorithm_id="notebook_checklist",
        tier_floor="free",
        default_layout_class="instruction_first",
        fingerprint=_fp(
            "notebook_checklist",
            cols=8,
            baseline=9.0,
            margin=0.08,
            regions=_REGIONS_INSTRUCTION,
            types=_TYPES_SERIF,
            encoding=("dash", "number", "label", "checkbox"),
            kinds=("execution",),
            rhythm="instruction_first_checklist",
        ),
        cover_subtitle="Modular Field Notes · Studio notebook",
        body_font="Times-Roman",
        mono_font="Courier",
        accent_hex="#B87333",
        paper_bias="warm",
        show_checklist=True,
    ),
    TemplateFamilyId.OSCILLOSCOPE_JOURNAL: FamilySpec(
        family_id=TemplateFamilyId.OSCILLOSCOPE_JOURNAL,
        display_name="Oscilloscope Journal",
        layout_algorithm_id="crt_bezel_frame",
        tier_floor="core",
        default_layout_class="performance_first",
        fingerprint=_fp(
            "crt_bezel_frame",
            cols=12,
            baseline=7.0,
            margin=0.04,
            regions=_REGIONS_PERF,
            types=("display", "body", "mono", "caption", "footer", "graticule"),
            encoding=("color", "dash", "number", "label", "trace"),
            kinds=("execution",),
            rhythm="performance_first_crt",
        ),
        cover_subtitle="Oscilloscope Journal · Trace log",
        body_font="Courier",
        mono_font="Courier",
        accent_hex="#00C896",
        paper_bias="dark",
    ),
    TemplateFamilyId.CIRCUIT_ARCHIVE: FamilySpec(
        family_id=TemplateFamilyId.CIRCUIT_ARCHIVE,
        display_name="Circuit Archive",
        layout_algorithm_id="title_block_engineering",
        tier_floor="free",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "title_block_engineering",
            cols=16,
            baseline=6.0,
            margin=0.04,
            regions=("title_block", "identity", "diagram", "bom", "construction", "footer"),
            types=("display", "body", "mono", "caption", "footer", "title_block"),
            encoding=("dash", "number", "label", "revision"),
            kinds=("execution",),
            rhythm="title_block_dense_engineering",
        ),
        cover_subtitle="Circuit Archive · Engineering plate",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#1A1A1A",
        paper_bias="vellum",
        show_title_block=True,
    ),
    TemplateFamilyId.MUSEUM_OF_SIGNAL: FamilySpec(
        family_id=TemplateFamilyId.MUSEUM_OF_SIGNAL,
        display_name="Museum of Signal",
        layout_algorithm_id="gallery_plate_mat",
        tier_floor="pro",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "gallery_plate_mat",
            cols=4,
            baseline=11.0,
            margin=0.14,
            regions=_REGIONS_PLATE + ("appendix_hook",),
            types=_TYPES_SERIF,
            encoding=("number", "label", "caption"),
            kinds=("plate", "appendix_execution"),
            rhythm="gallery_plate_caption",
        ),
        cover_subtitle="Museum of Signal · Collection",
        body_font="Times-Roman",
        mono_font="Courier",
        accent_hex="#8B919C",
        paper_bias="white",
    ),
    TemplateFamilyId.PATENT_FUTURE: FamilySpec(
        family_id=TemplateFamilyId.PATENT_FUTURE,
        display_name="Patent Future",
        layout_algorithm_id="figure_claims_two_col",
        tier_floor="core",
        default_layout_class="instruction_first",
        fingerprint=_fp(
            "figure_claims_two_col",
            cols=2,
            baseline=8.0,
            margin=0.07,
            regions=("identity", "figure", "claims", "disclaimer", "footer"),
            types=("display", "body", "mono", "caption", "footer", "claims"),
            encoding=("number", "label", "callout"),
            kinds=("execution",),
            rhythm="two_col_figure_claims",
        ),
        cover_subtitle="Document ID (not a patent)",
        body_font="Times-Roman",
        mono_font="Courier",
        accent_hex="#000000",
        paper_bias="white",
        patent_disclaimer=True,
    ),
    TemplateFamilyId.PATCH_CARTOGRAPHY: FamilySpec(
        family_id=TemplateFamilyId.PATCH_CARTOGRAPHY,
        display_name="Patch Cartography",
        layout_algorithm_id="seeded_force_cartography",
        tier_floor="pro",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "seeded_force_cartography",
            cols=12,
            baseline=8.0,
            margin=0.06,
            regions=("identity", "map_neatline", "itinerary", "legend", "footer"),
            types=_TYPES_STANDARD,
            encoding=("color", "dash", "number", "label", "route"),
            kinds=("execution",),
            rhythm="map_itinerary_routes",
        ),
        cover_subtitle="Patch Cartography · Signal routes",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#7B61FF",
        paper_bias="white",
    ),
    TemplateFamilyId.SONIC_BRUTALISM: FamilySpec(
        family_id=TemplateFamilyId.SONIC_BRUTALISM,
        display_name="Sonic Brutalism",
        layout_algorithm_id="brutalist_blocks",
        tier_floor="pro",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "brutalist_blocks",
            cols=4,
            baseline=12.0,
            margin=0.03,
            regions=("identity", "block_a", "block_b", "construction", "footer"),
            types=("display", "body", "mono", "footer", "heavy"),
            encoding=("dash", "number", "label"),
            kinds=("execution",),
            rhythm="brutalist_exposed_grid",
        ),
        cover_subtitle="Sonic Brutalism",
        body_font="Helvetica-Bold",
        mono_font="Courier",
        accent_hex="#E23D4A",
        paper_bias="white",
        require_full_cover_title=True,
    ),
    TemplateFamilyId.RITUAL_MACHINE: FamilySpec(
        family_id=TemplateFamilyId.RITUAL_MACHINE,
        display_name="Ritual Machine",
        layout_algorithm_id="radial_seal_frame",
        tier_floor="studio",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "radial_seal_frame",
            cols=8,
            baseline=9.0,
            margin=0.09,
            regions=("identity", "seal", "thresholds", "construction", "footer"),
            types=("display", "body", "mono", "caption", "footer", "seal"),
            encoding=("number", "label", "radial"),
            kinds=("plate", "appendix_execution"),
            rhythm="radial_threshold_seal",
        ),
        cover_subtitle="Ritual Machine · Thresholds",
        body_font="Times-Roman",
        mono_font="Courier",
        accent_hex="#7B61FF",
        paper_bias="dark",
    ),
    TemplateFamilyId.IMPOSSIBLE_INSTRUMENT: FamilySpec(
        family_id=TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
        display_name="Impossible Instrument",
        layout_algorithm_id="open_form_generative",
        tier_floor="studio",
        default_layout_class="diagram_first",
        fingerprint=_fp(
            "open_form_generative",
            cols=3,
            baseline=14.0,
            margin=0.15,
            regions=("identity", "plate", "atmosphere", "footer"),
            types=("display", "body", "mono", "caption", "footer", "experimental"),
            encoding=("number", "label"),
            kinds=("plate", "appendix_execution"),
            rhythm="open_form_generative_plate",
        ),
        cover_subtitle="Impossible Instrument · Art print",
        body_font="Helvetica",
        mono_font="Courier",
        accent_hex="#F5A623",
        paper_bias="dark",
    ),
}

PATENT_FUTURE_DISCLAIMER = (
    "This document is a PatchHive creative template. "
    "It is not a patent application, grant, or legal instrument."
)


def get_family(family_id: TemplateFamilyId | str) -> FamilySpec:
    if isinstance(family_id, str):
        family_id = TemplateFamilyId(family_id)
    try:
        return FAMILIES[family_id]
    except KeyError as exc:
        raise KeyError(f"unknown template family: {family_id}") from exc


def list_families() -> tuple[FamilySpec, ...]:
    return tuple(FAMILIES[k] for k in TemplateFamilyId)


def structural_fingerprint_distance(a: StructuralFingerprint, b: StructuralFingerprint) -> float:
    """Jaccard-ish distance over discrete fingerprint fields (0 identical, 1 fully different)."""
    if a.layout_algorithm_id == b.layout_algorithm_id:
        # Algorithms must differ for uniqueness — force high distance floor only if all else same
        algo_diff = 0.0
    else:
        algo_diff = 1.0

    def jaccard(x: tuple[str, ...], y: tuple[str, ...]) -> float:
        sx, sy = set(x), set(y)
        if not sx and not sy:
            return 0.0
        inter = len(sx & sy)
        union = len(sx | sy)
        return 1.0 - (inter / union)

    parts = [
        algo_diff,
        jaccard(a.region_graph, b.region_graph),
        jaccard(a.type_role_set, b.type_role_set),
        jaccard(a.diagram_encoding, b.diagram_encoding),
        jaccard(a.default_page_kinds, b.default_page_kinds),
        0.0 if a.rhythm_signature == b.rhythm_signature else 1.0,
        0.0 if a.grid_modules[0] == b.grid_modules[0] else 0.5,
    ]
    return sum(parts) / len(parts)


def pairwise_fingerprint_distances() -> list[tuple[str, str, float]]:
    ids = list(TemplateFamilyId)
    out: list[tuple[str, str, float]] = []
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            d = structural_fingerprint_distance(
                FAMILIES[left].fingerprint, FAMILIES[right].fingerprint
            )
            out.append((left.value, right.value, d))
    return out


def assert_families_structurally_unique(min_distance: float = STRUCT_MIN_DISTANCE) -> None:
    failures = [(a, b, d) for a, b, d in pairwise_fingerprint_distances() if d < min_distance]
    if failures:
        detail = ", ".join(f"{a}/{b}={d:.2f}" for a, b, d in failures)
        raise AssertionError(f"family fingerprint distance < {min_distance}: {detail}")
