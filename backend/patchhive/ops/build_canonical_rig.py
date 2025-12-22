from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import (
    CanonicalJack,
    CanonicalModule,
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    NormalledEdge,
    ObservedPlacement,
    Provenance,
    ProvenanceType,
    RigSpec,
)


class BuildCanonicalRigError(Exception):
    pass


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_inferred(evidence_ref: str, confidence: float = 0.9) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
                method="build_canonical_rig",
            )
        ],
        confidence=confidence,
        status=FieldStatus.inferred,
    )


def _meta_confirmed(evidence_ref: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.gallery,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )


def _load_gallery_entry(
    store: ModuleGalleryStore,
    gallery_module_id: str,
    gallery_rev: Optional[datetime],
) -> Tuple[datetime, object]:
    """
    Returns (rev, ModuleGalleryEntry)
    - If gallery_rev is None, uses latest
    - If gallery_rev provided, loads that exact revision (must exist)
    """
    if gallery_rev is None:
        latest = store.get_latest(gallery_module_id)
        if latest is None:
            raise BuildCanonicalRigError(f"Gallery module not found: {gallery_module_id}")
        return latest.rev, latest

    # Load exact revision
    revs = store.list_revisions(gallery_module_id)
    if not revs:
        raise BuildCanonicalRigError(f"Gallery module not found: {gallery_module_id}")

    # Find matching rev by parsing filename expectation (store uses rev timestamp in filename).
    # We simply load all and pick exact rev match (deterministic but not super fast; fine for v1).
    for p in revs:
        entry = store.load_revision(gallery_module_id, p)
        if entry.rev == gallery_rev:
            return entry.rev, entry

    raise BuildCanonicalRigError(
        f"Gallery rev not found: {gallery_module_id} @ {gallery_rev.isoformat()}"
    )


def build_canonical_rig(
    rig: RigSpec,
    *,
    gallery_store: ModuleGalleryStore,
) -> CanonicalRig:
    """
    Build CanonicalRig from RigSpec + Module Gallery.

    Determinism rules:
    - module order in output is stable by instance_id
    - jacks order is stable by jack_id
    - normalled_edges order stable by (from_jack,to_jack)

    VL2 rules:
    - semi-normalled paths MUST be explicit in rig.normalled_edges (builder carries them through)
    - modes are carried from gallery into CanonicalModule for later mode selection in PatchGraph
    """
    # Resolve modules
    canonical_modules: List[CanonicalModule] = []

    # Stable ordering
    modules_sorted = sorted(rig.modules, key=lambda m: m.instance_id)

    for inst in modules_sorted:
        rev, g = _load_gallery_entry(gallery_store, inst.gallery_module_id, inst.gallery_rev)

        # Canonicalize jacks in stable order
        g_jacks_sorted = sorted(g.jacks, key=lambda j: j.jack_id)
        c_jacks: List[CanonicalJack] = []
        for j in g_jacks_sorted:
            c_jacks.append(
                CanonicalJack(
                    jack_id=j.jack_id,
                    label=j.label,
                    dir=j.dir,
                    signal=j.signal,
                    meta=j.meta,
                )
            )

        # Preserve observed placement if present
        obs: Optional[ObservedPlacement] = inst.observed_placement

        canonical_modules.append(
            CanonicalModule(
                instance_id=inst.instance_id,
                module_gallery_id=g.module_gallery_id,
                module_rev=rev,
                name=g.name,
                manufacturer=g.manufacturer,
                hp=g.hp,
                tags=list(g.tags),
                power=g.power,
                jacks=c_jacks,
                modes=list(g.modes),
                observed_placement=obs,
                meta=inst.meta,  # instance meta (source of instance binding)
            )
        )

    # Carry through explicit normalled edges (VL2 critical)
    edges_sorted = sorted(rig.normalled_edges, key=lambda e: (e.from_jack, e.to_jack))
    c_edges: List[NormalledEdge] = []
    for e in edges_sorted:
        c_edges.append(e)

    # Provenance: builder adds a derived marker + keeps rig provenance
    prov = list(rig.provenance)
    prov.append(
        Provenance(
            type=ProvenanceType.derived,
            timestamp=_now_utc(),
            evidence_ref=f"rig:{rig.rig_id}",
            method="build_canonical_rig",
        )
    )

    return CanonicalRig(
        rig_id=rig.rig_id,
        name=rig.name,
        modules=canonical_modules,
        normalled_edges=c_edges,
        provenance=prov,
    )
