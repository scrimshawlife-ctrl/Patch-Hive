from __future__ import annotations

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import (
    CanonicalRig,
    CanonicalRigJack,
    CanonicalRigModule,
    RigSpec,
)


def build_canonical_rig(rig: RigSpec, *, gallery_store: ModuleGalleryStore) -> CanonicalRig:
    """
    Deterministic build placeholder for canonical rig creation.
    """
    modules: list[CanonicalRigModule] = []
    for module_gallery_id in rig.module_gallery_ids:
        entry = gallery_store.get_latest(module_gallery_id)
        if entry is None:
            raise ValueError(f"Module not found in gallery: {module_gallery_id}")
        jacks = [
            CanonicalRigJack(
                jack_id=jack.jack_id,
                label=jack.label,
                dir=jack.dir,
                signal=jack.signal,
            )
            for jack in entry.jacks
        ]
        modules.append(
            CanonicalRigModule(
                instance_id=module_gallery_id,
                name=entry.canonical_name,
                hp=entry.hp or 0,
                jacks=jacks,
            )
        )
    return CanonicalRig(rig_id=rig.rig_id, modules=modules)
