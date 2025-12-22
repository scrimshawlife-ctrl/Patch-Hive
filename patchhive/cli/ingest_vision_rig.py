from __future__ import annotations

import json
from pathlib import Path

from patchhive.vision.gemini_interface import VisionRigSpec, VisionModuleHit
from patchhive.gallery.function_store import FunctionRegistryStore
from patchhive.gallery.sketch_store import ModuleSketchStore
from patchhive.ops.vision_to_rigspec import vision_to_rigspec
from patchhive.schemas import RigSpec


def _rigspec_to_dict(rig: RigSpec) -> dict:
    return {
        "rig_id": rig.rig_id,
        "name": rig.name,
        "source": rig.source.value,
        "modules": [
            {
                "instance_id": m.instance_id,
                "gallery_module_id": m.gallery_module_id,
                "gallery_rev": m.gallery_rev.isoformat() if m.gallery_rev else None,
                "observed_placement": m.observed_placement,
            }
            for m in rig.modules
        ],
        "normalled_edges": [
            {
                "from_jack": e.from_jack,
                "to_jack": e.to_jack,
                "behavior": e.behavior.value,
            }
            for e in rig.normalled_edges
        ],
        "notes": list(rig.notes),
    }


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--vision-json", required=True)
    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--out-rigspec", required=True)
    args = ap.parse_args()

    payload = json.loads(Path(args.vision_json).read_text(encoding="utf-8"))
    vision = VisionRigSpec(
        rig_id=payload["rig_id"],
        evidence_ref=payload["evidence_ref"],
        modules=[
            VisionModuleHit(
                module_name=mod["module_name"],
                manufacturer=mod.get("manufacturer"),
                hp=mod.get("hp"),
                jack_labels=list(mod.get("jack_labels", [])),
            )
            for mod in payload.get("modules", [])
        ],
    )

    fn_store = FunctionRegistryStore(args.gallery_root)
    sketch_store = ModuleSketchStore(args.gallery_root)

    from patchhive.gallery.store import ModuleGalleryStore

    gallery = ModuleGalleryStore(args.gallery_root)

    def lookup(name: str, manufacturer: str | None):
        return gallery.find_by_name(name=name, manufacturer=manufacturer)

    def upsert(entry):
        gallery.append_revision(entry)

    rig = vision_to_rigspec(
        vision,
        gallery_lookup_fn=lookup,
        gallery_upsert_fn=upsert,
        function_store=fn_store,
        sketch_store=sketch_store,
    )

    Path(args.out_rigspec).write_text(
        json.dumps(_rigspec_to_dict(rig), indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Wrote RigSpec: {args.out_rigspec}")


if __name__ == "__main__":
    main()
