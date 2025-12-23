"""Deterministic plain sketch renderer."""

from __future__ import annotations

from typing import List, Tuple

from patchhive.schemas import ModuleGalleryEntry


def render_module_sketch_svg(
    entry: ModuleGalleryEntry,
    *,
    width_px: int = 260,
    header_px: int = 36,
    jack_radius: int = 8,
    padding: int = 12,
    cols: int = 2,
) -> str:
    """
    Deterministic, plain SVG sketch:
    - outer box
    - title
    - jack circles in a simple grid
    - jack labels (small)
    No styling dependencies, no randomness.
    """
    jacks = sorted(entry.jacks, key=lambda jack: jack.jack_id or jack.name)
    rows = max(1, (len(jacks) + cols - 1) // cols)
    row_h = 28
    height_px = header_px + padding + rows * row_h + padding

    def xy(i: int) -> Tuple[int, int]:
        r = i // cols
        c = i % cols
        x = padding + c * (width_px // cols)
        y = header_px + padding + r * row_h
        return x, y

    def esc(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts: List[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width_px}" height="{height_px}" '
        f'viewBox="0 0 {width_px} {height_px}">'
    )
    parts.append(
        f'<rect x="1" y="1" width="{width_px-2}" height="{height_px-2}" '
        'fill="white" stroke="black" stroke-width="2"/>'
    )
    parts.append(
        f'<text x="{padding}" y="{padding+14}" font-family="monospace" font-size="12">'
        f"{esc(entry.manufacturer)} — {esc(entry.name)} ({entry.hp}hp)</text>"
    )
    parts.append(
        f'<line x1="{padding}" y1="{header_px-6}" '
        f'x2="{width_px-padding}" y2="{header_px-6}" stroke="black" stroke-width="1"/>'
    )

    for i, jack in enumerate(jacks):
        x, y = xy(i)
        cx = x + jack_radius
        cy = y + jack_radius
        label = jack.label or jack.name
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{jack_radius}" '
            'fill="none" stroke="black" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{cx + jack_radius + 8}" y="{cy + 4}" '
            f'font-family="monospace" font-size="10">{esc(label)}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)
