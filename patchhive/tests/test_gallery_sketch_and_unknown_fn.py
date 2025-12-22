from __future__ import annotations

from pathlib import Path

from patchhive.gallery.function_store import FunctionRegistryStore
from patchhive.gallery.sketch_store import ModuleSketchStore
from patchhive.vision.gemini_interface import VisionRigSpec, VisionModuleHit
from patchhive.ops.vision_to_rigspec import vision_to_rigspec


def test_unknown_jacks_create_registry_entries(tmp_path: Path) -> None:
    fn_store = FunctionRegistryStore(str(tmp_path))
    sketch_store = ModuleSketchStore(str(tmp_path))

    vision = VisionRigSpec(
        rig_id="rig.test",
        evidence_ref="vision:test",
        modules=[
            VisionModuleHit(
                module_name="Voltage Lab 2",
                manufacturer="Pittsburgh Modular",
                hp=104,
                jack_labels=["CLK OUT", "GATE IN", "FN 1", "WEIRD JACK XYZ"],
            )
        ],
    )

    def lookup(name, manufacturer):
        return None

    def upsert(entry):
        return None

    vision_to_rigspec(
        vision,
        gallery_lookup_fn=lookup,
        gallery_upsert_fn=upsert,
        function_store=fn_store,
        sketch_store=sketch_store,
    )

    reg = fn_store.get()
    assert any(fid.startswith("fn.unknown.") for fid in reg.functions.keys())

    sk_dir = Path(tmp_path) / "sketches"
    assert sk_dir.exists()
