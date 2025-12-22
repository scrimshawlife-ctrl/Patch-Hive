from __future__ import annotations

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import CanonicalRig, RigSpec


def build_canonical_rig(rig: RigSpec, gallery_store: ModuleGalleryStore) -> CanonicalRig:
    modules = [
        gallery_store.to_canonical(module_spec.gallery_module_id, module_spec.instance_id)
        for module_spec in rig.modules
    ]
    return CanonicalRig(rig_id=rig.rig_id, modules=modules)
