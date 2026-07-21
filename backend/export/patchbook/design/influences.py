"""Style influence mixer: conflict groups + sparse transfer functions."""

from __future__ import annotations

from dataclasses import dataclass

from export.patchbook.design.recipe import StyleWeights, influence_ids

# Primary conflict groups (design §A.5) — disjoint primary membership
INFLUENCE_GROUPS: dict[str, tuple[str, ...]] = {
    "g_density": (
        "engineering",
        "scientific",
        "technical_manual",
        "archival",
        "patent",
        "data_visualization",
    ),
    "g_minimal": ("minimal", "swiss", "open_form_zero_state"),
    "g_ornate": ("luxury", "ritual", "record_packaging", "organic", "biomorphic"),
    "g_signal": (
        "circuit_board",
        "oscilloscope",
        "cyber_hive",
        "modular_synth",
        "blueprint",
    ),
    "g_space": ("architectural", "museum", "field_notebook"),
    "g_expression": (
        "editorial",
        "brutalist",
        "symbolic",
        "abstract",
        "surreal",
        "futurist",
        "retro_futurist",
        "analog_studio",
        "generative_geometry",
    ),
}


@dataclass(frozen=True)
class NormalizedInfluences:
    raw: dict[str, int]
    normalized: dict[str, float]  # 0–1 after group L1 normalize
    group_sums: dict[str, int]


def normalize_influences(influences: dict[str, int]) -> NormalizedInfluences:
    """L1-normalize within conflict groups when sum > 100; drop zeros."""
    allowed = set(influence_ids())
    cleaned = {k: int(v) for k, v in influences.items() if k in allowed and int(v) > 0}
    normalized: dict[str, float] = {}
    group_sums: dict[str, int] = {}

    claimed: set[str] = set()
    for group_id in sorted(INFLUENCE_GROUPS):
        members = INFLUENCE_GROUPS[group_id]
        active = {m: cleaned[m] for m in members if m in cleaned}
        total = sum(active.values())
        group_sums[group_id] = total
        if total <= 0:
            continue
        scale = 100.0 / total if total > 100 else 1.0
        for name, weight in active.items():
            # Primary membership only
            if name in claimed:
                continue
            claimed.add(name)
            # normalized 0–1 relative to post-scale weight / 100
            scaled = weight * scale
            normalized[name] = min(1.0, scaled / 100.0)

    # Any influence not in a group: scale alone if >100 else raw/100
    for name, weight in cleaned.items():
        if name in claimed:
            continue
        normalized[name] = min(1.0, weight / 100.0)

    return NormalizedInfluences(raw=cleaned, normalized=normalized, group_sums=group_sums)


@dataclass(frozen=True)
class EffectiveStyleParams:
    weights: StyleWeights
    ornamentation_eff: float
    technical_density_eff: float
    white_space_eff: float
    diagram_token_set: str
    color_mode_bias: str
    margin_scale: float


def apply_influence_transfers(
    weights: StyleWeights,
    normalized: dict[str, float],
) -> EffectiveStyleParams:
    """Sparse influence → parameter transfer (design §A.5)."""
    minimal = normalized.get("minimal", 0.0)
    tm = normalized.get("technical_manual", 0.0)
    cyber = normalized.get("cyber_hive", 0.0)
    blueprint = normalized.get("blueprint", 0.0)
    brutalist = normalized.get("brutalist", 0.0)
    museum = normalized.get("museum", 0.0)

    ornamentation_eff = weights.ornamentation * (1.0 - 0.6 * minimal)
    technical_density_eff = min(100.0, weights.technical_density + 20.0 * tm)
    white_space_eff = max(0.0, weights.white_space - 15.0 * brutalist + 10.0 * museum)
    margin_scale = 1.0 + 0.15 * minimal + 0.1 * museum

    if cyber >= blueprint and cyber > 0:
        diagram_token_set = "cyber_hive"
        color_mode_bias = "amber_cyan"
    elif blueprint > 0:
        diagram_token_set = "orthogonal_schematic"
        color_mode_bias = "bw"
    else:
        diagram_token_set = "default"
        color_mode_bias = "print_safe"

    return EffectiveStyleParams(
        weights=weights,
        ornamentation_eff=ornamentation_eff,
        technical_density_eff=technical_density_eff,
        white_space_eff=white_space_eff,
        diagram_token_set=diagram_token_set,
        color_mode_bias=color_mode_bias,
        margin_scale=margin_scale,
    )
