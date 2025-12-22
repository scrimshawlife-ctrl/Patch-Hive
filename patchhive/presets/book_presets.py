from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class BookPreset:
    book_id: str
    title: str
    category_weights: Dict[str, float]
    difficulty_weights: Dict[str, float]
    max_total: int
    max_per_category: int


def vl2_starter_book() -> BookPreset:
    return BookPreset(
        book_id="vl2.starter",
        title="Voltage Lab 2 — Starter Book",
        category_weights={
            "Voice": 2.4,
            "Utility": 1.2,
            "Study": 1.1,
            "Clock-Rhythm": 1.2,
            "Generative": 0.6,
            "Performance Macro": 0.8,
            "Texture-FX": 0.8,
        },
        difficulty_weights={"Beginner": 2.2, "Intermediate": 1.0, "Advanced": 0.5, "Experimental": 0.4},
        max_total=80,
        max_per_category=36,
    )


def vl2_performance_book() -> BookPreset:
    return BookPreset(
        book_id="vl2.performance",
        title="Voltage Lab 2 — Performance Macros",
        category_weights={
            "Performance Macro": 3.0,
            "Voice": 1.6,
            "Clock-Rhythm": 1.2,
            "Generative": 0.8,
            "Utility": 0.5,
            "Study": 0.3,
            "Texture-FX": 1.2,
        },
        difficulty_weights={"Beginner": 1.0, "Intermediate": 1.5, "Advanced": 1.0, "Experimental": 0.7},
        max_total=70,
        max_per_category=40,
    )
