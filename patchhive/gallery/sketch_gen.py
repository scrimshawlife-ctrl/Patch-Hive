from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from patchhive.schemas_gallery import (
    ModuleSketch,
    JackSketch,
    FieldMeta,
    Provenance,
    ProvenanceType,
    FieldStatus,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta(method: str, evidence_ref: str, ptype: ProvenanceType) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(type=ptype, timestamp=_now_utc(), evidence_ref=evidence_ref, method=method)
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )


def generate_plain_module_sketch(
    *,
    module_key: str,
    hp: int,
    jack_labels: List[str],
    evidence_ref: str,
    jack_count: int | None = None,
    width_px: int = 512,
    height_px: int = 768,
) -> ModuleSketch:
    """
    Deterministic sketch:
      - module rectangle
      - jack dots in a single grid region (bottom 60%)
      - labels under each dot
    """
    # layout grid
    pad = 40
    top = 90
    usable_w = width_px - 2 * pad
    usable_h = height_px - top - pad

    labels = list(jack_labels)
    if not labels:
        if jack_count and jack_count > 0:
            labels = ["UNCONFIRMED"] * jack_count
        else:
            labels = []

    # jacks arranged in rows of 6
    cols = 6
    n = max(1, len(labels))
    rows = (n + cols - 1) // cols

    x_step = usable_w / (cols + 1)
    y_step = usable_h / (rows + 1)

    jacks: List[JackSketch] = []
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}">',
        f'<rect x="0" y="0" width="{width_px}" height="{height_px}" fill="white"/>',
        (
            f'<rect x="{pad}" y="{top}" width="{width_px-2*pad}" '
            f'height="{height_px-top-pad}" stroke="black" stroke-width="3" fill="#f7f7f7"/>'
        ),
        f'<text x="{pad}" y="54" font-size="22" font-family="monospace">{module_key}</text>',
        f'<text x="{pad}" y="78" font-size="14" font-family="monospace">HP={hp}</text>',
    ]

    meta = _meta("generate_plain_module_sketch.v1", evidence_ref, ProvenanceType.derived)

    for idx, lbl in enumerate(labels):
        r = idx // cols
        c = idx % cols
        x = pad + (c + 1) * x_step
        y = top + (r + 1) * y_step

        jack_id = f"jack.{idx:02d}"
        jacks.append(JackSketch(jack_id=jack_id, label=lbl, x=float(x), y=float(y), meta=meta))

        svg_parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" stroke="black" '
            f'stroke-width="3" fill="white"/>'
        )
        svg_parts.append(
            f'<text x="{x-26:.1f}" y="{y+28:.1f}" font-size="10" '
            f'font-family="monospace">{(lbl or "")[:12]}</text>'
        )

    svg_parts.append("</svg>")
    svg = "\n".join(svg_parts)

    if not labels:
        svg = svg.replace(
            "</svg>",
            (
                f'<text x="{pad}" y="{height_px - pad / 2:.1f}" '
                f'font-size="12" font-family="monospace" fill="#555">UNCONFIRMED</text>\n</svg>'
            ),
        )

    return ModuleSketch(
        module_key=module_key,
        hp=hp,
        jacks=jacks,
        svg=svg,
        width_px=width_px,
        height_px=height_px,
        meta=meta,
    )
