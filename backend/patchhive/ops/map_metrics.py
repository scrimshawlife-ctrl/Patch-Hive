"""Map canonical rig to capability metrics."""

from __future__ import annotations

from collections import defaultdict

from patchhive.schemas import CanonicalRig, RigMetricsCategory, RigMetricsPacket

CATEGORY_MAP = {
    "source": RigMetricsCategory.SOURCES,
    "shaper": RigMetricsCategory.SHAPERS,
    "controller": RigMetricsCategory.CONTROLLERS,
    "modulator": RigMetricsCategory.MODULATORS,
    "router": RigMetricsCategory.ROUTERS_MIX,
    "mix": RigMetricsCategory.ROUTERS_MIX,
    "clock": RigMetricsCategory.CLOCK_DOMAIN,
    "fx": RigMetricsCategory.FX_SPACE,
    "space": RigMetricsCategory.FX_SPACE,
    "io": RigMetricsCategory.IO_EXTERNAL,
    "normal": RigMetricsCategory.NORMALS_INTERNAL_BUSSES,
}


def _category_for_profile(profile: str) -> RigMetricsCategory:
    key = profile.lower()
    return CATEGORY_MAP.get(key, RigMetricsCategory.SHAPERS)


def map_metrics_v1(canonical: CanonicalRig) -> RigMetricsPacket:
    categories: dict[RigMetricsCategory, list[str]] = defaultdict(list)
    for module in canonical.modules:
        for section in module.module_spec.sections:
            for capability in section.capability_profile:
                category = _category_for_profile(capability)
                categories[category].append(module.module_spec.name)
    summary = {category.value: len(modules) for category, modules in categories.items()}
    return RigMetricsPacket(rig_id=canonical.rig_id, categories=categories, summary=summary)
