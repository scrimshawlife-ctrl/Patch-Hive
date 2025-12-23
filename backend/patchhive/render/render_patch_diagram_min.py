from __future__ import annotations

from patchhive.schemas import CanonicalRig
from patchhive.schemas_library import PatchDiagram


def render_patch_diagram_min(
    canon: CanonicalRig,
    patch,
    *,
    width: int = 1024,
    height: int = 768,
) -> PatchDiagram:
    """
    Minimal SVG:
    - list cables as text
    - show module names as a vertical list
    """
    mods = sorted(canon.modules, key=lambda m: m.instance_id)
    cable_lines = [
        f"{cable.type.value}: {cable.from_jack} -> {cable.to_jack}" for cable in patch.cables
    ]

    y = 40
    lines = []
    lines.append(f'<text x="20" y="{y}" font-size="20">Patch: {patch.patch_id}</text>')
    y += 30
    lines.append(f'<text x="20" y="{y}" font-size="16">Rig: {canon.rig_id}</text>')
    y += 40

    lines.append(f'<text x="20" y="{y}" font-size="18">Modules</text>')
    y += 26
    for module in mods:
        lines.append(
            f'<text x="30" y="{y}" font-size="14">{module.instance_id}: {module.name}</text>'
        )
        y += 18

    y += 20
    lines.append(f'<text x="20" y="{y}" font-size="18">Cables</text>')
    y += 26
    for cable in cable_lines:
        lines.append(f'<text x="30" y="{y}" font-size="14">{cable}</text>')
        y += 18

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>'
        f"{''.join(lines)}"
        "</svg>"
    )

    return PatchDiagram(patch_id=patch.patch_id, svg=svg, width=width, height=height)
