from __future__ import annotations

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from patchhive.render.diagram_scene import DiagramScene


def draw_scene_pdf(c: canvas.Canvas, scene: DiagramScene, *, title: str) -> None:
    width, height = landscape(letter)
    sx = width / scene.width
    sy = height / scene.height
    scale = min(sx, sy)

    def tx(x: float) -> float:
        return x * scale

    def ty(y: float) -> float:
        return height - (y * scale)

    c.setFont("Courier", 14)
    c.drawString(24, height - 24, title)

    c.setLineWidth(2)
    for cb in scene.cables:
        (x1, y1), (xm, ym), (x2, y2) = cb.points
        c.bezier(tx(x1), ty(y1), tx(xm), ty(ym), tx(xm), ty(ym), tx(x2), ty(y2))

    c.setLineWidth(2)
    for module in scene.modules:
        c.rect(tx(module.x), ty(module.y + module.h), tx(module.w), tx(module.h), stroke=1, fill=0)
        c.setFont("Courier", 10)
        c.drawString(tx(module.x + 10), ty(module.y + 18), module.title[:60])
        c.setFont("Courier", 8)
        c.drawString(tx(module.x + 10), ty(module.y + 36), module.instance_id[:60])

        for jack in module.jacks.values():
            r = 6 * scale
            c.circle(tx(jack.x), ty(jack.y), r, stroke=1, fill=0)
            c.setFont("Courier", 6)
            c.drawString(tx(jack.x - 18), ty(jack.y - 10), (jack.label or "")[:12])

    c.setFont("Courier", 10)
    c.drawString(24, 80, "Cables:")
    y = 66
    c.setFont("Courier", 7)
    for line in scene.legend_lines[:20]:
        c.drawString(24, y, line[:160])
        y -= 10
        if y < 24:
            break
