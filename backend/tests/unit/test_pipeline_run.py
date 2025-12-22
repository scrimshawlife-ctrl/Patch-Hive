from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from patchhive.fixtures.basic_voice_fixture import gallery_voice_entry, rigspec_voice_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.pipeline.run import run_pipeline
from patchhive.schemas import FieldMeta, FieldStatus, PatchIntent, Provenance, ProvenanceType


def _intent() -> PatchIntent:
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, tzinfo=timezone.utc),
                evidence_ref="test:intent",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )
    return PatchIntent(archetype="generative_mod", energy="medium", focus="learnability", meta=meta)


def test_pipeline_bundle(tmp_path: Path) -> None:
    gallery = ModuleGalleryStore(tmp_path / "gallery")
    gallery.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    bundle = run_pipeline(
        rig=rig,
        gallery_root=str(tmp_path / "gallery"),
        intent=_intent(),
        seed=101,
        image_id="img.test",
    )

    assert bundle.rig_id == rig.rig_id
    assert bundle.patch.rig_id == rig.rig_id
    assert len(bundle.layouts) == 3
    assert bundle.envelope.patch_id == bundle.patch.patch_id
