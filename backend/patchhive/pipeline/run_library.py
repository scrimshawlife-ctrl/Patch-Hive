from __future__ import annotations

from patchhive.ops.build_patch_library import build_patch_library
from patchhive.render.render_patch_diagram_min import render_patch_diagram_min
from patchhive.schemas import CanonicalRig
from patchhive.schemas_library import PatchLibrary, PatchSpaceConstraints
from patchhive.templates.registry import build_default_registry


def run_library(
    canon: CanonicalRig,
    *,
    constraints: PatchSpaceConstraints,
    include_diagrams: bool = True,
) -> PatchLibrary:
    registry = build_default_registry()
    library = build_patch_library(canon, registry=registry, constraints=constraints)

    if include_diagrams:
        new_items = []
        for item in library.patches:
            diagram = render_patch_diagram_min(canon, item.patch)
            new_items.append(item.model_copy(update={"diagram": diagram}))
        library = library.model_copy(update={"patches": new_items})

    return library
