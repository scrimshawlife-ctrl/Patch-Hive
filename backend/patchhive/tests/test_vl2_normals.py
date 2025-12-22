from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.generate_patch import generate_patch
from patchhive.schemas import ModuleGalleryEntry, JackSpec, ModeProfile, ProvenanceRecord


def test_vl2_normals_and_modes() -> None:
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    entry = ModuleGalleryEntry(
        module_gallery_id="vl2-1",
        rev=timestamp,
        name="VL2 Core",
        manufacturer="AAL",
        hp=20,
        power=None,
        jacks=[
            JackSpec(
                jack_id="out",
                label="OUT",
                name="out",
                signal_type="audio",
                direction="output",
                normalled_to="in",
            ),
            JackSpec(jack_id="in", label="IN", name="in", signal_type="audio", direction="input"),
        ],
        modes=[ModeProfile(name="A", capability_profile=["Sources"])],
        images=[],
        sketch_svg=None,
        provenance=[
            ProvenanceRecord(
                type="manual",
                model_version=None,
                timestamp=timestamp,
                evidence_ref="vl2",
            )
        ],
        notes=["vl2 normals"],
    )
    rig = build_canonical_rig("rig-vl2", [entry])
    assert rig.explicit_normalled_edges
    edge = rig.explicit_normalled_edges[0]
    assert edge.break_on_insert is True
    patch_graph, _, _, _, _ = generate_patch(rig, seed=0)
    assert patch_graph.mode_selections[rig.modules[0].stable_id] == "A"
