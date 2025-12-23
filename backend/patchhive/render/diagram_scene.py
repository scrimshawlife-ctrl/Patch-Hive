from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from patchhive.schemas import CanonicalRig, PatchGraph, SuggestedLayout


@dataclass(frozen=True)
class SceneJack:
    key: str
    x: float
    y: float
    label: str


@dataclass(frozen=True)
class SceneModule:
    instance_id: str
    title: str
    x: float
    y: float
    w: float
    h: float
    jacks: Dict[str, SceneJack]


@dataclass(frozen=True)
class SceneCable:
    cable_type: str
    from_key: str
    to_key: str
    points: List[Tuple[float, float]]


@dataclass(frozen=True)
class DiagramScene:
    width: int
    height: int
    modules: List[SceneModule]
    cables: List[SceneCable]
    legend_lines: List[str]


def _jack_key(jack: object) -> str:
    if isinstance(jack, str):
        return jack
    if hasattr(jack, "as_str"):
        return jack.as_str()
    if hasattr(jack, "instance_id") and hasattr(jack, "jack_id"):
        return f"{jack.instance_id}::{jack.jack_id}"
    return str(jack)

def build_scene(
    canon: CanonicalRig,
    patch: PatchGraph,
    *,
    layout: Optional[SuggestedLayout] = None,
    width: int = 1600,
    height: int = 900,
    hp_scale: float = 8.0,
    row_y: float = 120.0,
    module_h: float = 220.0,
) -> DiagramScene:
    """
    Deterministic sketch layout.
    """
    mods = sorted(canon.modules, key=lambda m: m.instance_id)

    x_map: Dict[str, float] = {}
    if layout is not None and layout.placements:
        for placement in layout.placements:
            x_map[placement.instance_id] = 60.0 + (placement.x_hp * hp_scale)
    else:
        cursor = 60.0
        for module in mods:
            x_map[module.instance_id] = cursor
            cursor += (module.hp * hp_scale) + 30.0

    modules: List[SceneModule] = []
    jack_pos: Dict[str, Tuple[float, float, str]] = {}

    for module in mods:
        x = x_map.get(module.instance_id, 60.0)
        y = row_y
        w = max(40.0, float(module.hp) * hp_scale)
        h = module_h

        js = sorted(module.jacks, key=lambda j: j.jack_id)
        n = max(1, len(js))
        pad = 16.0
        span = max(1.0, (w - 2 * pad))
        step = span / (n + 1)

        jacks: Dict[str, SceneJack] = {}
        for i, jack in enumerate(js, start=1):
            key = _jack_key(jack.jack_id)
            if hasattr(jack, "instance_id") and hasattr(jack, "jack_id"):
                key = _jack_key(jack)

            jx = x + pad + (i * step)
            jy = y + h - 24.0
            label = jack.label or jack.jack_id
            scene_jack = SceneJack(key=key, x=jx, y=jy, label=label)
            jacks[key] = scene_jack
            jack_pos[key] = (jx, jy, label)

        modules.append(
            SceneModule(
                instance_id=module.instance_id,
                title=f"{module.name}",
                x=x,
                y=y,
                w=w,
                h=h,
                jacks=jacks,
            )
        )

    cables: List[SceneCable] = []
    legend: List[str] = []
    for cable in patch.cables:
        from_key = _jack_key(cable.from_jack)
        to_key = _jack_key(cable.to_jack)

        if from_key not in jack_pos or to_key not in jack_pos:
            legend.append(f"[MISSING JACK] {cable.type.value}: {from_key} -> {to_key}")
            continue

        x1, y1, _ = jack_pos[from_key]
        x2, y2, _ = jack_pos[to_key]

        mid_y = min(y1, y2) - 120.0
        pts = [(x1, y1), ((x1 + x2) / 2.0, mid_y), (x2, y2)]

        cables.append(
            SceneCable(
                cable_type=cable.type.value,
                from_key=from_key,
                to_key=to_key,
                points=pts,
            )
        )
        legend.append(f"{cable.type.value}: {from_key} -> {to_key}")

    return DiagramScene(
        width=width,
        height=height,
        modules=modules,
        cables=cables,
        legend_lines=legend,
    )
