from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from patchhive.schemas import (
    JackDir,
    ModuleGalleryEntry,
    ModuleJack,
    PowerSpec,
    RigModuleInstance,
    RigSource,
    RigSpec,
    SignalContract,
    SignalKind,
    SignalRate,
)
from patchhive.gallery.function_store import FunctionRegistryStore
from patchhive.gallery.sketch_gen import generate_plain_module_sketch
from patchhive.gallery.sketch_store import ModuleSketchStore
from patchhive.vision.gemini_interface import VisionRigSpec


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _signal_kind_from_label(label: str) -> str:
    low = label.lower()
    if "pitch" in low or "v/oct" in low:
        return "pitch_cv"
    if "clock" in low or "clk" in low:
        return "clock"
    if "gate" in low:
        return "gate"
    if "trig" in low or "trigger" in low:
        return "trigger"
    if "cv" in low or "fm" in low:
        return "cv"
    if "audio" in low or "out" in low:
        return "audio"
    return "unknown"


def _dir_from_label(label: str) -> str:
    low = label.lower()
    if "in" in low or "cv" in low or "fm" in low or "gate" in low or "trig" in low or "clk" in low:
        return "in"
    return "out"


def _contract_from_label(label: str) -> SignalContract:
    kind_str = _signal_kind_from_label(label)
    kind = SignalKind[kind_str] if kind_str in SignalKind.__members__ else SignalKind.unknown
    rate = SignalRate.control if kind != SignalKind.audio else SignalRate.audio
    return SignalContract(kind=kind, rate=rate, range_v=None, polarity="unknown", meta=None)


def vision_to_rigspec(
    vision: VisionRigSpec,
    *,
    gallery_lookup_fn,
    gallery_upsert_fn,
    function_store: FunctionRegistryStore,
    sketch_store: ModuleSketchStore,
) -> RigSpec:
    """
    Build RigSpec from vision extraction:
    - find module entries in gallery
    - if missing, derive minimal entry + sketch + add to gallery
    - detect unknown/proprietary jack names -> ensure_unknown() in function registry
    """
    instances: List[RigModuleInstance] = []

    for idx, hit in enumerate(vision.modules, start=1):
        entry: Optional[ModuleGalleryEntry] = gallery_lookup_fn(hit.module_name, hit.manufacturer)

        hp = hit.hp or (entry.hp if entry else 0) or 10
        jack_labels = hit.jack_labels or ([j.label for j in entry.jacks] if entry else [])

        if entry is None:
            module_key = (
                f"gallery.{(hit.manufacturer or 'unknown').lower()}."
                f"{hit.module_name.lower().replace(' ', '_')}.{hp}hp"
            )
            jack_specs: List[ModuleJack] = []
            for jlbl in jack_labels:
                direction = _dir_from_label(jlbl)
                signal_kind = _signal_kind_from_label(jlbl)

                function_store.ensure_unknown(
                    label=jlbl or "Unknown",
                    direction=direction,
                    signal_kind=signal_kind,
                    evidence_ref=vision.evidence_ref,
                )

                jack_specs.append(
                    ModuleJack(
                        jack_id=f"j{len(jack_specs):02d}",
                        label=jlbl or "Unknown",
                        dir=JackDir.in_ if direction == "in" else JackDir.out,
                        signal=_contract_from_label(jlbl or ""),
                        meta=None,
                    )
                )

            sketch = generate_plain_module_sketch(
                module_key=module_key,
                hp=hp,
                jack_labels=jack_labels,
                evidence_ref=vision.evidence_ref,
            )
            sketch_store.write(sketch)

            entry = ModuleGalleryEntry(
                module_gallery_id=module_key,
                rev=_now_utc(),
                name=hit.module_name,
                manufacturer=hit.manufacturer or "Unknown",
                hp=hp,
                tags=[],
                power=PowerSpec(plus12_ma=None, minus12_ma=None, plus5_ma=None, meta=None),
                jacks=jack_specs,
                modes=[],
                images=[],
                sketch_svg=sketch.svg,
                provenance=[],
                notes=["Derived from vision input."],
            )
            gallery_upsert_fn(entry)
        else:
            module_key = entry.module_gallery_id
            if sketch_store.read(module_key) is None:
                labels = [j.label for j in entry.jacks]
                sketch = generate_plain_module_sketch(
                    module_key=module_key,
                    hp=entry.hp,
                    jack_labels=labels,
                    evidence_ref=vision.evidence_ref,
                )
                sketch_store.write(sketch)

            for j in entry.jacks:
                lbl = j.label or j.jack_id
                if function_store.lookup_alias(lbl) is None:
                    direction = "in" if j.dir == JackDir.in_ else "out"
                    kind = j.signal.kind.value if hasattr(j.signal.kind, "value") else str(j.signal.kind)
                    function_store.ensure_unknown(
                        label=lbl,
                        direction=direction,
                        signal_kind=kind,
                        evidence_ref=vision.evidence_ref,
                    )

        instances.append(
            RigModuleInstance(
                instance_id=f"inst.vision.{idx:02d}",
                gallery_module_id=module_key,
                gallery_rev=None,
                observed_placement=None,
                meta=None,
            )
        )

    return RigSpec(
        rig_id=vision.rig_id,
        name=vision.rig_id,
        source=RigSource.manual_picklist,
        modules=instances,
        normalled_edges=[],
        provenance=[],
        notes=[f"vision:{vision.evidence_ref}"],
    )
