from __future__ import annotations

from datetime import datetime, timezone

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.ensure_gallery_sketch import ensure_sketch
from patchhive.schemas import FieldMeta, FieldStatus, ModuleGalleryEntry, Provenance, ProvenanceType


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def bind_function_id_to_jack_append_only(
    store: ModuleGalleryStore,
    *,
    module_gallery_id: str,
    jack_id: str,
    function_id: str,
    evidence_ref: str,
) -> ModuleGalleryEntry:
    """
    Append-only revision that sets SignalContract.function_id for the specified jack.
    """
    latest = store.get_latest(module_gallery_id)
    if latest is None:
        raise ValueError(f"Module not found: {module_gallery_id}")

    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
                method="bind_function_id_to_jack_append_only",
            )
        ],
        confidence=0.98,
        status=FieldStatus.confirmed,
    )

    changed = False
    new_jacks = []
    for j in latest.jacks:
        if j.jack_id == jack_id:
            sig = j.signal.model_copy(update={"function_id": function_id, "meta": meta})
            new_jacks.append(j.model_copy(update={"signal": sig}))
            changed = True
        else:
            new_jacks.append(j)

    if not changed:
        raise ValueError(f"Jack not found on module {module_gallery_id}: {jack_id}")

    updated = latest.model_copy(
        update={
            "rev": _now_utc(),
            "jacks": new_jacks,
        }
    )
    updated = ensure_sketch(updated)
    store.append_revision(updated)
    return updated
