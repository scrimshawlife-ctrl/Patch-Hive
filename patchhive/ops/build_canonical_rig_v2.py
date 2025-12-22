from __future__ import annotations

from typing import List

from patchhive.schemas import CanonicalRig, CanonicalModule, CanonicalJack, JackDir, SignalContract, SignalKind, SignalRate
from patchhive.schemas_rigspec_v2 import RigSpecV2
from patchhive.gallery.store import ModuleGalleryStore


def build_canonical_rig_v2(rig: RigSpecV2, *, gallery_store: ModuleGalleryStore) -> CanonicalRig:
    """
    Builds CanonicalRig using gallery definitions.
    If rig module has override_jack_labels, apply them (best-effort) to produce placeholder jacks.
    """
    canon_mods: List[CanonicalModule] = []

    for inst in rig.modules:
        # Try to get entry from gallery (may not exist for unknown modules)
        try:
            entry = gallery_store.get_module(inst.module_key)
        except KeyError:
            entry = None

        # if override exists, use that instead of gallery jack list (when gallery incomplete)
        if inst.override_jack_labels:
            jacks = []
            for i, lbl in enumerate(inst.override_jack_labels):
                jacks.append(CanonicalJack(
                    jack_id=f"ovr.{i:02d}",
                    label=lbl,
                    # direction/signal kind remain unknown until reviewed
                    dir=JackDir.bidir,
                    signal=SignalContract(kind=SignalKind.unknown, rate=SignalRate.control, range_v=None, polarity="unknown", meta=None),
                ))
        elif entry:
            jacks = [
                CanonicalJack(
                    jack_id=jack.jack_id,
                    label=jack.label,
                    dir=jack.dir,
                    signal=jack.signal,
                )
                for jack in entry.jacks
            ]
        else:
            # No gallery entry and no override - empty jacks
            jacks = []

        canon_mods.append(CanonicalModule(
            instance_id=inst.instance_id,
            name=inst.display_name,
            hp=inst.hp,
            jacks=jacks,
            tags=[],
            modes=[],
        ))

    return CanonicalRig(rig_id=rig.rig_id, modules=canon_mods)
