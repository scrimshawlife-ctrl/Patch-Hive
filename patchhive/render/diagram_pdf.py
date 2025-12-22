from __future__ import annotations

from typing import Dict

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from patchhive.render.diagram_scene import CABLE_COLOR


def _hex_color(value: str) -> colors.Color:
    value = value.lstrip("#")
    r = int(value[0:2], 16) / 255.0
    g = int(value[2:4], 16) / 255.0
    b = int(value[4:6], 16) / 255.0
    return colors.Color(r, g, b)


def draw_scene_pdf(c: canvas.Canvas, scene: Dict[str, object], *, title: str) -> None:
    width = float(scene["width"])
    height = float(scene["height"])

    c.setFillColor(colors.black)
    c.setFont("Courier-Bold", 14)
    c.drawString(24, height - 28, title[:120])

    # Modules
    c.setFont("Courier", 8)
    for mod in scene["modules"]:
        x = mod["x"]
        y = mod["y"]
        w = mod["w"]
        h = mod["h"]
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.rect(x, y, w, h, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.drawString(x + 6, y + h - 12, mod["id"])
        for _, (jx, jy, label) in mod["jacks"].items():
            c.circle(jx, jy, 2.5, stroke=1, fill=0)
            c.drawString(jx - 6, jy - 12, label[:10])

    # Cables
    for cable in scene["cables"]:
        color = _hex_color(CABLE_COLOR.get(cable["type"], "#333333"))
        c.setStrokeColor(color)
        points = cable["points"]
        if len(points) < 2:
            continue
        path = c.beginPath()
        path.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            path.lineTo(px, py)
        c.drawPath(path, stroke=1, fill=0)
