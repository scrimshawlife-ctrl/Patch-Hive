from __future__ import annotations

from typing import Any, Dict

from patchhive.schemas import CanonicalRig, PatchGraph


CABLE_COLOR = {
    "audio": "#000000",
    "pitch_cv": "#2b6cff",
    "gate": "#ff9f1c",
    "trigger": "#ff9f1c",
    "clock": "#d43f3a",
    "cv": "#2b6cff",
}


def build_scene(
    canon: CanonicalRig,
    patch: PatchGraph,
    *,
    layout: Any,
    width: int = 1600,
    height: int = 1000,
    hp_scale: float = 8.0,
    row_y: float = 100.0,
    module_h: float = 220.0,
) -> Dict[str, Any]:
    """
    Multi-row, print-safe deterministic diagram builder.
    """
    row_gap = 60.0
    row_height = module_h + row_gap

    modules = []
    jack_pos: Dict[str, tuple[float, float, int]] = {}

    def jack_key(jack_id: str) -> str:
        return jack_id

    for p in layout.placements:
        m = next(m for m in canon.modules if m.instance_id == p.instance_id)

        x = 60.0 + (p.x_hp * hp_scale)
        y = row_y + (p.row * row_height)
        w = max(40.0, m.hp * hp_scale)

        js = sorted(m.jacks, key=lambda j: j.jack_id)
        pad = 16.0
        step = max(1.0, (w - 2 * pad) / (len(js) + 1))

        scene_jacks: Dict[str, tuple[float, float, str]] = {}
        for i, j in enumerate(js, start=1):
            key = jack_key(j.jack_id)
            jx = x + pad + (i * step)
            jy = y + module_h - 24.0
            if key not in jack_pos:
                jack_pos[key] = (jx, jy, p.row)
            scene_jacks[key] = (jx, jy, j.label)

        modules.append(
            {
                "id": m.instance_id,
                "x": x,
                "y": y,
                "w": w,
                "h": module_h,
                "jacks": scene_jacks,
            }
        )

    cables = []
    for c in patch.cables:
        fk = jack_key(c.from_jack)
        tk = jack_key(c.to_jack)

        if fk not in jack_pos or tk not in jack_pos:
            continue

        x1, y1, r1 = jack_pos[fk]
        x2, y2, r2 = jack_pos[tk]

        lane_y = min(y1, y2) - (80 + 20 * abs(r1 - r2))

        cables.append(
            {
                "type": c.type.value,
                "points": [
                    (x1, y1),
                    (x1, lane_y),
                    (x2, lane_y),
                    (x2, y2),
                ],
            }
        )

    return {
        "width": width,
        "height": height,
        "modules": modules,
        "cables": cables,
    }
