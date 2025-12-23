from __future__ import annotations

from typing import Iterable

from .models import PatchBookDocument


def _ensure_steps(steps: Iterable[int]) -> None:
    required = set(range(7))
    missing = required.difference(steps)
    if missing:
        raise ValueError(f"Missing patching order steps: {sorted(missing)}")


def assert_patchbook_contract(document: PatchBookDocument) -> None:
    branding = document.branding
    if not branding or not branding.wordmark_svg:
        raise ValueError("PatchBook branding asset missing")

    for page in document.pages:
        schematic = page.schematic
        if not schematic.diagram_svg and not schematic.wiring_list:
            raise ValueError(f"Patch {page.header.patch_id} missing schematic/wiring fallback")

        steps = [step.step for step in page.patching_order.steps]
        _ensure_steps(steps)
