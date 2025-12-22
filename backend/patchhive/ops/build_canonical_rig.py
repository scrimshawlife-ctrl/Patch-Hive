"""Build CanonicalRig representation."""
from __future__ import annotations

import hashlib
from typing import Dict, List

from core.discovery import register_function
from patchhive.schemas import (
    CanonicalRig,
    ModuleGalleryEntry,
    ModuleInstance,
    NormalledEdge,
)


CAPABILITY_CATEGORIES = [
    "Sources",
    "Shapers",
    "Controllers",
    "Modulators",
    "Routers / Mix",
    "Clock Domain",
    "FX / Space",
    "IO / External",
    "Normals / Internal Busses",
]


def _stable_id(module_id: str, index: int) -> str:
    seed = f"{module_id}:{index}".encode()
    return hashlib.sha256(seed).hexdigest()[:12]


def _categorize(entry: ModuleGalleryEntry) -> List[str]:
    name = entry.name.lower()
    categories: List[str] = []
    if any(token in name for token in ["osc", "vco", "voice", "noise", "drum"]):
        categories.append("Sources")
    if any(token in name for token in ["filter", "wave", "shape", "fold", "distort"]):
        categories.append("Shapers")
    if any(token in name for token in ["env", "envelope", "adsr", "control"]):
        categories.append("Controllers")
    if any(token in name for token in ["lfo", "mod", "random", "chaos"]):
        categories.append("Modulators")
    if any(token in name for token in ["mix", "vca", "router", "switch"]):
        categories.append("Routers / Mix")
    if any(token in name for token in ["clock", "seq", "trigger"]):
        categories.append("Clock Domain")
    if any(token in name for token in ["delay", "reverb", "fx", "space"]):
        categories.append("FX / Space")
    if any(token in name for token in ["io", "input", "output", "midi"]):
        categories.append("IO / External")
    if any(jack.normalled_to for jack in entry.jacks):
        categories.append("Normals / Internal Busses")
    if not categories:
        categories.append("Routers / Mix")
    return categories


def _build_normalled_edges(stable_id: str, entry: ModuleGalleryEntry) -> List[NormalledEdge]:
    edges: List[NormalledEdge] = []
    for jack in entry.jacks:
        if jack.normalled_to:
            edges.append(
                NormalledEdge(
                    from_jack=f"{stable_id}:{jack.name}",
                    to_jack=f"{stable_id}:{jack.normalled_to}",
                    break_on_insert=True,
                )
            )
    return edges


def build_canonical_rig(rig_id: str, modules: List[ModuleGalleryEntry]) -> CanonicalRig:
    module_instances: List[ModuleInstance] = []
    explicit_signal_contracts: List[str] = []
    explicit_normalled_edges: List[NormalledEdge] = []
    capability_surface: Dict[str, int] = {category: 0 for category in CAPABILITY_CATEGORIES}

    for index, entry in enumerate(sorted(modules, key=lambda e: e.module_gallery_id)):
        stable_id = _stable_id(entry.module_gallery_id, index)
        categories = _categorize(entry)
        normalled_edges = _build_normalled_edges(stable_id, entry)
        for category in categories:
            capability_surface[category] += 1
        module_instances.append(
            ModuleInstance(
                stable_id=stable_id,
                gallery_entry=entry,
                capability_categories=categories,
                normalled_edges=normalled_edges,
            )
        )
        for jack in entry.jacks:
            explicit_signal_contracts.append(
                f"{stable_id}:{jack.name}:{jack.direction}:{jack.signal_type}"
            )
        explicit_normalled_edges.extend(normalled_edges)

    stable_ids = [module.stable_id for module in module_instances]

    return CanonicalRig(
        rig_id=rig_id,
        stable_ids=stable_ids,
        explicit_signal_contracts=sorted(explicit_signal_contracts),
        explicit_normalled_edges=explicit_normalled_edges,
        capability_surface=capability_surface,
        modules=module_instances,
    )


register_function(
    name="build_canonical_rig",
    function=build_canonical_rig,
    description="Build CanonicalRig with explicit normalled edges and capability surface.",
    input_model="rig_id, List[ModuleGalleryEntry]",
    output_model="CanonicalRig",
)
