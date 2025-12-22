from __future__ import annotations

from pathlib import Path

from patchhive.fixtures.basic_voice_fixture import gallery_voice_entry, rigspec_voice_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.generate_patch import generate_patch
from patchhive.ops.map_metrics import map_metrics
from patchhive.schemas import FieldMeta, FieldStatus, PatchIntent, Provenance, ProvenanceType


def _intent(archetype: str) -> PatchIntent:
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=__import__("datetime").datetime(
                    2025, 12, 21, 0, 0, 0, tzinfo=__import__("datetime").timezone.utc
                ),
                evidence_ref="test:intent",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )
    return PatchIntent(archetype=archetype, energy="medium", focus="learnability", meta=meta)


def test_generate_basic_voice_is_deterministic(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    canon = build_canonical_rig(rig, gallery_store=store)
    _ = map_metrics(canon)

    out1 = generate_patch(canon, intent=_intent("basic_voice"), seed=123)
    out2 = generate_patch(canon, intent=_intent("basic_voice"), seed=123)

    assert out1["patch"].to_canonical_json() == out2["patch"].to_canonical_json()
    assert out1["plan"].to_canonical_json() == out2["plan"].to_canonical_json()
    assert out1["validation"].to_canonical_json() == out2["validation"].to_canonical_json()
    assert len(out1["variations"]) >= 1


def test_generate_clocked_sequence_has_clock_route_when_available(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    out = generate_patch(canon, intent=_intent("clocked_sequence"), seed=7)
    cables = [(c.type.value, c.from_jack, c.to_jack) for c in out["patch"].cables]

    # Expect a clock cable if both ends exist
    assert any(t == "clock" for (t, _, _) in cables)
    # Ritual time present
    assert out["patch"].timeline.sections == ["prep", "threshold", "peak", "release", "seal"]
