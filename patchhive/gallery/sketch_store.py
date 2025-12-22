from __future__ import annotations

from pathlib import Path

import json

from patchhive.schemas_gallery import ModuleSketch


class ModuleSketchStore:
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.sketch_dir = self.root / "sketches"
        self.sketch_dir.mkdir(parents=True, exist_ok=True)

    def write(self, sketch: ModuleSketch) -> None:
        base = self.sketch_dir / sketch.module_key
        base.mkdir(parents=True, exist_ok=True)
        (base / "sketch.json").write_text(
            json.dumps(sketch.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (base / "sketch.svg").write_text(sketch.svg, encoding="utf-8")

    def read(self, module_key: str) -> ModuleSketch | None:
        base = self.sketch_dir / module_key
        p = base / "sketch.json"
        if not p.exists():
            return None
        return ModuleSketch.model_validate_json(p.read_text(encoding="utf-8"))
