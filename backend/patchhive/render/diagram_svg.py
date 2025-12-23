from __future__ import annotations

from typing import List

from patchhive.render.diagram_scene import DiagramScene


def scene_to_svg(scene: DiagramScene) -> str:
    width, height = scene.width, scene.height

    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts: List[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>')

    for cable in scene.cables:
        (x1, y1), (xm, ym), (x2, y2) = cable.points
        parts.append(
            f'<path d="M {x1:.1f} {y1:.1f} Q {xm:.1f} {ym:.1f} {x2:.1f} {y2:.1f}" '
            f'stroke="black" stroke-width="2" fill="none"/>'
        )

    for module in scene.modules:
        parts.append(
            f'<rect x="{module.x:.1f}" y="{module.y:.1f}" width="{module.w:.1f}" '
            f'height="{module.h:.1f}" stroke="black" stroke-width="2" fill="#f7f7f7"/>'
        )
        parts.append(
            f'<text x="{module.x + 10:.1f}" y="{module.y + 24:.1f}" font-size="16" '
            f'font-family="monospace">{esc(module.title)}</text>'
        )
        parts.append(
            f'<text x="{module.x + 10:.1f}" y="{module.y + 44:.1f}" font-size="12" '
            f'font-family="monospace">{esc(module.instance_id)}</text>'
        )

        for jack in module.jacks.values():
            parts.append(
                f'<circle cx="{jack.x:.1f}" cy="{jack.y:.1f}" r="6" stroke="black" '
                f'stroke-width="2" fill="white"/>'
            )
            parts.append(
                f'<text x="{jack.x - 18:.1f}" y="{jack.y + 20:.1f}" font-size="10" '
                f'font-family="monospace">{esc(jack.label)}</text>'
            )

    lx, ly = 60, scene.height - 220
    parts.append(f'<text x="{lx}" y="{ly}" font-size="16" font-family="monospace">Cables</text>')
    y = ly + 24
    for line in scene.legend_lines[:30]:
        parts.append(
            f'<text x="{lx}" y="{y}" font-size="10" font-family="monospace">{esc(line)}</text>'
        )
        y += 14

    parts.append("</svg>")
    return "\n".join(parts)
