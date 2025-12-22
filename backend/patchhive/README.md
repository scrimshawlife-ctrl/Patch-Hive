# PatchHive RigSpec Pipeline

This module implements PatchHive’s deterministic RigSpec ingestion, normalization, metric mapping, and patch generation pipeline with VL2-format modeling.

## Usage

### 1) Detect modules from a photo

```python
from patchhive.ops.detect_from_photo import GeminiFixtureClient, detect_modules_from_photo_v1
from patchhive.schemas import DetectedModule, Provenance, ProvenanceType, ProvenanceStatus, ProvenancedValue

fixtures = [
    DetectedModule(
        detection_id="det-01",
        name=ProvenancedValue(
            value="VL2 Function Generator",
            provenance=Provenance(type=ProvenanceType.GEMINI),
            confidence=0.92,
            status=ProvenanceStatus.INFERRED,
        ),
        confidence=0.92,
    )
]
client = GeminiFixtureClient(fixtures)
photo_bytes = b"fixture"
modules = detect_modules_from_photo_v1(photo_bytes, client)
```

### 2) Resolve modules against the gallery

```python
from patchhive.ops.resolve_modules import resolve_modules_v1
from patchhive.gallery.store import ModuleGalleryStore

store = ModuleGalleryStore(pathlib.Path("gallery.jsonl"))
entries = list(store.iter_entries())
resolved = resolve_modules_v1(modules, entries)
```

### 3) Ensure module specs + append-only gallery revisions

```python
from patchhive.ops.ensure_specs import ensure_module_specs_v1

result = ensure_module_specs_v1(resolved, entries)
for entry in result.new_entries:
    store.append(entry)
```

### 4) Build the canonical rig + map metrics

```python
from patchhive.ops.build_canonical_rig import build_canonical_rig_v1
from patchhive.ops.map_metrics import map_metrics_v1
from patchhive.schemas import RigSpec, RigModuleInput, ProvenancedValue, Provenance, ProvenanceType, ProvenanceStatus

rig_spec = RigSpec(
    rig_id="rig-001",
    modules=[
        RigModuleInput(
            module_id=None,
            name=ProvenancedValue(
                value="VL2 Function Generator",
                provenance=Provenance(type=ProvenanceType.MANUAL),
                confidence=1.0,
                status=ProvenanceStatus.CONFIRMED,
            ),
        )
    ],
)
canonical = build_canonical_rig_v1(rig_spec, result.resolved)
metrics = map_metrics_v1(canonical)
```

### 5) Suggest layouts

```python
from patchhive.ops.suggest_layouts import suggest_layouts_v1

layouts = suggest_layouts_v1(canonical, user_profile="performer", seed=11)
```

### 6) Generate a patch + validate

```python
from patchhive.ops.generate_patch import generate_patch_v1
from patchhive.ops.validate_patch import validate_patch_v1

patch_graph, patch_plan, variations = generate_patch_v1(
    rig_id=canonical.rig_id,
    intent="Evolving modulated texture",
    seed=42,
    module_ids=[module.canonical_id for module in canonical.modules],
    normalled_edges=canonical.normalled_edges,
)
report = validate_patch_v1(patch_graph)
```

## Notes
- All inferred fields carry provenance, confidence, and status metadata.
- Gallery revisions are append-only; new revisions reference previous revisions.
- VL2 normalled edges are modeled explicitly with `break_on_insert`.
- Patch graphs include timeline phases: prep → threshold → peak → release → seal.
