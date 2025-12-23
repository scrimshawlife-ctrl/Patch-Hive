from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.generate_patch import generate_patch
from patchhive.schemas import ModuleGalleryEntry, JackSpec, ProvenanceRecord


def _module_entry(module_id: str, name: str) -> ModuleGalleryEntry:
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return ModuleGalleryEntry(
        module_gallery_id=module_id,
        rev=timestamp,
        name=name,
        manufacturer="AAL",
        hp=10,
        power=None,
        jacks=[
            JackSpec(jack_id="out", label="OUT", name="out", signal_type="audio", direction="output"),
            JackSpec(jack_id="in", label="IN", name="in", signal_type="audio", direction="input"),
        ],
        modes=None,
        images=[],
        sketch_svg=None,
        provenance=[
            ProvenanceRecord(
                type="manual",
                model_version=None,
                timestamp=timestamp,
                evidence_ref="seed",
            )
        ],
        notes=[],
    )


def test_determinism_patch_generation() -> None:
    modules = [_module_entry("mod-1", "Osc"), _module_entry("mod-2", "Filter")]
    rig = build_canonical_rig("rig-1", modules)
    result_a = generate_patch(rig, seed=42)
    result_b = generate_patch(rig, seed=42)
    assert result_a[0].model_dump() == result_b[0].model_dump()
    assert result_a[1].model_dump() == result_b[1].model_dump()
    assert result_a[2].model_dump() == result_b[2].model_dump()
    assert result_a[3][0].model_dump() == result_b[3][0].model_dump()
