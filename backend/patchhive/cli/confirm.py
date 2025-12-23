from __future__ import annotations

import json
from pathlib import Path

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.commit_function_registry import confirm_and_commit_function
from patchhive.ops.commit_jack_function_to_module import bind_function_id_to_jack_append_only
from patchhive.ops.commit_module_image import attach_module_image_append_only
from patchhive.registry.function_store import JackFunctionStore
from patchhive.schemas import JackFunctionEntry, VisionRigDetection


def _load_detection(path: str | Path) -> VisionRigDetection:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return VisionRigDetection.model_validate(raw)


def _prompt_yes_no(msg: str, default_no: bool = True) -> bool:
    suffix = " [y/N]: " if default_no else " [Y/n]: "
    ans = input(msg + suffix).strip().lower()
    if ans == "" and default_no:
        return False
    if ans == "" and not default_no:
        return True
    return ans.startswith("y")


def run_confirm_cli(
    *,
    detection_json_path: str,
    gallery_root: str,
    function_registry_root: str,
) -> None:
    det = _load_detection(detection_json_path)
    gallery = ModuleGalleryStore(gallery_root)
    fnstore = JackFunctionStore(function_registry_root)

    print("\n=== PatchHive Phase 8 Confirmation ===")
    print(f"Image: {det.image_id}")
    print(f"Detected modules: {len(det.detected_modules)}")
    print(f"Proposed functions: {len(det.proposed_functions)}\n")

    for fn in det.proposed_functions:
        assert isinstance(fn, JackFunctionEntry)
        print("\nProposed Function:")
        print(f"  id: {fn.function_id}")
        print(f"  name: {fn.canonical_name}")
        print(f"  desc: {fn.description}")
        print(f"  kind_hint: {fn.kind_hint.value}")
        print(f"  aliases: {fn.label_aliases}")

        if _prompt_yes_no("Confirm and commit this function?"):
            committed = confirm_and_commit_function(
                fnstore,
                fn,
                evidence_ref=f"confirm:image:{det.image_id}:function:{fn.function_id}",
            )
            print(f"  ✅ committed rev={committed.rev.isoformat()}")
        else:
            print("  ⛔ skipped")

    for m in det.detected_modules:
        print(
            f"\nModule proposal: {m.brand_guess or 'unknown'} {m.label_guess} "
            f"(temp_id={m.temp_id})"
        )
        if _prompt_yes_no("Attach an image to an existing gallery module id?"):
            module_gallery_id = input(
                "  Enter gallery module id (e.g., mod.erica.vl2.core): "
            ).strip()
            image_url = input("  Enter image url/path (stored as ref): ").strip()
            updated = attach_module_image_append_only(
                gallery,
                module_gallery_id=module_gallery_id,
                image_url=image_url,
                kind="manual_upload",
                evidence_ref=f"confirm:image:{det.image_id}:module_image",
            )
            print(f"  ✅ module updated rev={updated.rev.isoformat()} images={len(updated.images)}")

    if det.proposed_functions and _prompt_yes_no(
        "\nBind a confirmed function_id to a specific module jack now?"
    ):
        module_gallery_id = input("  Enter gallery module id: ").strip()
        jack_id = input("  Enter jack_id (exact): ").strip()
        function_id = input("  Enter function_id (confirmed): ").strip()
        updated = bind_function_id_to_jack_append_only(
            gallery,
            module_gallery_id=module_gallery_id,
            jack_id=jack_id,
            function_id=function_id,
            evidence_ref=f"confirm:image:{det.image_id}:bind_fn",
        )
        print(f"  ✅ module updated rev={updated.rev.isoformat()}")

    print("\n=== Done. Canon updated append-only where confirmed. ===\n")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--detection", required=True, help="Path to VisionRigDetection JSON")
    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--function-root", required=True)
    args = ap.parse_args()

    run_confirm_cli(
        detection_json_path=args.detection,
        gallery_root=args.gallery_root,
        function_registry_root=args.function_root,
    )
