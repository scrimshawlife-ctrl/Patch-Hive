from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.validate_patch import validate_patch
from patchhive.schemas import (
    JackSpec,
    ModuleGalleryEntry,
    PatchCable,
    PatchGraph,
    PatchNode,
    ProvenanceRecord,
)


def test_validation_flags_illegal_connections() -> None:
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    entry = ModuleGalleryEntry(
        module_gallery_id="mod-1",
        rev=timestamp,
        name="Osc",
        manufacturer="AAL",
        hp=8,
        power=None,
        jacks=[
            JackSpec(
                jack_id="out", label="OUT", name="out", signal_type="audio", direction="output"
            ),
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
                evidence_ref="validation",
            )
        ],
        notes=[],
    )
    rig = build_canonical_rig("rig-validate", [entry])
    patch = PatchGraph(
        nodes=[PatchNode(module_id=rig.modules[0].stable_id, label="Osc")],
        cables=[
            PatchCable(
                from_module_id=rig.modules[0].stable_id,
                from_port="in",
                to_module_id=rig.modules[0].stable_id,
                to_port="out",
                cable_type="audio",
            )
        ],
        macros=[],
        timeline=["prep", "threshold", "peak", "release"],
        mode_selections={},
    )
    report = validate_patch(patch, rig)
    assert report.illegal_connections
    assert report.stability_score < 0.5
