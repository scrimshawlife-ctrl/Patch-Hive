from __future__ import annotations

from pydantic import BaseModel, Field


class E2EPreset(str):
    # mirrors your library_presets
    starter = "starter"
    core = "core"
    deep = "deep"


class E2EConfig(BaseModel):
    gallery_root: str
    out_dir: str
    preset: str = E2EPreset.core

    # case layout (diagram rendering)
    rows: int = 1
    row_hp: int = 104

    # pruning knobs (book shaping)
    max_total: int = 160
    max_per_category: int = 70
    drop_runaway: bool = True
    drop_silence: bool = False

    # weights (JSON strings or dicts; keep simple here as dicts)
    category_weights: dict = Field(default_factory=lambda: {
        "Voice": 2.0,
        "Clock-Rhythm": 1.4,
        "Generative": 0.8,
        "Performance Macro": 1.0,
        "Texture-FX": 1.0,
        "Utility": 0.6,
        "Study": 0.7,
    })
    difficulty_weights: dict = Field(default_factory=lambda: {
        "Beginner": 2.0,
        "Intermediate": 1.2,
        "Advanced": 0.9,
        "Experimental": 0.5,
    })

    # diagram/export toggles
    include_svgs: bool = True
    include_pdf: bool = True
    interactive_pdf: bool = True
