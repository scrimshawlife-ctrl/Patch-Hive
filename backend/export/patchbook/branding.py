"""Branding tokens and wordmark for PatchBook exports."""

from __future__ import annotations

from pathlib import Path

from .models import PatchBookBranding, PATCHBOOK_TEMPLATE_VERSION

BRAND_PRIMARY = "#111827"
BRAND_ACCENT = "#F59E0B"
BRAND_FONT = "Helvetica"

WORDMARK_SVG = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<svg width=\"220\" height=\"40\" viewBox=\"0 0 220 40\" xmlns=\"http://www.w3.org/2000/svg\">
  <g fill=\"{accent}\">
    <polygon points=\"16,6 24,10 24,20 16,24 8,20 8,10\" />
    <polygon points=\"32,16 40,20 40,30 32,34 24,30 24,20\" />
  </g>
  <text x=\"54\" y=\"26\" font-family=\"{font}\" font-size=\"20\" fill=\"{primary}\" font-weight=\"700\">PatchHive</text>
</svg>
"""


def _load_logo_svg() -> str | None:
    """Return a logo SVG if one exists in the repo."""
    candidate_paths = [
        Path("frontend/public/patchhive-logo.svg"),
        Path("frontend/public/logo.svg"),
        Path("frontend/public/favicon.svg"),
    ]
    for path in candidate_paths:
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def get_patchbook_branding() -> PatchBookBranding:
    """Build PatchBook branding metadata."""
    logo_svg = _load_logo_svg()
    wordmark_svg = None
    if logo_svg and "PatchHive" in logo_svg:
        wordmark_svg = logo_svg
    else:
        wordmark_svg = WORDMARK_SVG.format(primary=BRAND_PRIMARY, accent=BRAND_ACCENT, font=BRAND_FONT)

    return PatchBookBranding(
        primary_color=BRAND_PRIMARY,
        accent_color=BRAND_ACCENT,
        font_family=BRAND_FONT,
        template_version=PATCHBOOK_TEMPLATE_VERSION,
        wordmark_svg=wordmark_svg,
    )
