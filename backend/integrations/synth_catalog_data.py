"""
Synth Catalog Research bridge for PatchHive.

Source: Abraxas modular-synth-catalog-research (PR #984) sealed research packet.
Provenance: OBSERVED/INFERRED via multi-source rotation (official, retailer, community).
ABX-Core v1.3 aligned — unknown HP/power remain null (never invented).

Default seed: data/synth-catalog/seed-phase2-v1.json
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

# Repo root relative to backend/integrations/
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED_PATH = _REPO_ROOT / "data" / "synth-catalog" / "seed-phase2-v1.json"

SOURCE_NAME = "SynthCatalogResearch"
SOURCE_REFERENCE_DEFAULT = "data/synth-catalog/seed-phase2-v1.json"

# Major brands from research Phase 2 (class-level coverage target)
MAJOR_BRANDS: List[str] = [
    "2hp",
    "4ms Company",
    "ALM Busy Circuits",
    "Acid Rain Technology",
    "ADDAC System",
    "Befaco",
    "Doepfer",
    "Bastl Instruments",
    "Cwejman",
    "Dreadbox",
    "Erica Synths",
    "Endorphin.es",
    "Expert Sleepers",
    "Intellijel",
    "Make Noise",
    "Mutable Instruments",
    "Behringer",
    "Noise Engineering",
    "Pittsburgh Modular",
    "Qu-Bit Electronix",
    "Rossum Electro-Music",
    "TipTop Audio",
    "Verbos Electronics",
    "WMD",
    "Winterbloom",
    "Xaoc Devices",
    "Zlob Modular",
    "ZVEX Modular",
    "Instruo",
]

# Curated full-spec modules (power/I/O only when research or manufacturer data recorded them)
SYNTH_CATALOG_MODULES: List[Dict[str, Any]] = [
    {
        "brand": "Noise Engineering",
        "name": "Basimilus Iteritas Alter",
        "hp": 10,
        "module_type": "VCO",
        "power_12v_ma": 70,
        "power_neg12v_ma": 10,
        "io_ports": [
            {"name": "Pitch", "type": "cv_in"},
            {"name": "Trig", "type": "gate_in"},
            {"name": "Out", "type": "audio_out"},
        ],
        "tags": ["drum", "percussion", "digital"],
        "description": "Digital drum voice",
        "manufacturer_url": "https://noiseengineering.us/",
        "source": SOURCE_NAME,
        "source_reference": "phase2-major-brands.md",
    },
    {
        "brand": "Make Noise",
        "name": "Maths",
        "hp": 20,
        "module_type": "UTIL",
        "power_12v_ma": 60,
        "power_neg12v_ma": 50,
        "io_ports": [
            {"name": "CH1", "type": "cv_in"},
            {"name": "SUM", "type": "cv_out"},
        ],
        "tags": ["function generator"],
        "description": "Analog computer / function generator",
        "manufacturer_url": "https://www.makenoisemusic.com/",
        "source": SOURCE_NAME,
        "source_reference": "phase2-major-brands.md",
    },
    {
        "brand": "Instruo",
        "name": "arbhar",
        "hp": 18,
        "module_type": "SAMP",
        "power_12v_ma": 120,
        "power_neg12v_ma": 15,
        "io_ports": [
            {"name": "In", "type": "audio_in"},
            {"name": "Out", "type": "audio_out"},
        ],
        "tags": ["granular"],
        "description": "Granular processor",
        "manufacturer_url": "https://www.instruomodular.com/",
        "source": SOURCE_NAME,
        "source_reference": "phase2-major-brands.md",
    },
]


def map_category(raw: str) -> str:
    """Map free-text research categories onto PatchHive module_type taxonomy."""
    r = (raw or "").lower()
    rules = [
        (("oscillator", "vco", "sound source", "wavetable"), "VCO"),
        (("filter", "vcf"), "VCF"),
        (("vca",), "VCA"),
        (("envelope", "function generator"), "ENV"),
        (("lfo",), "LFO"),
        (("sequencer", "clock", "quantizer", "sample and hold"), "SEQ"),
        (
            (
                "effect",
                "distortion",
                "reverb",
                "delay",
                "waveshaper",
                "equalizer",
                "fuzz",
                "lo-fi",
            ),
            "FX",
        ),
        (("mixer", "mix", "panning"), "MIX"),
        (("sampl", "granular", ".wav", "wav player"), "SAMP"),
        (("midi",), "MIDI"),
    ]
    for keys, cat in rules:
        if any(k in r for k in keys):
            return cat
    return "UTIL"


def map_availability(status: str) -> str:
    """Map research status text to catalog is_available values."""
    s = (status or "").replace("*", "").strip().lower()
    if "discontinu" in s:
        return "discontinued"
    if "upcoming" in s or "announce" in s:
        return "upcoming"
    return "available"


@lru_cache(maxsize=4)
def load_seed(path: Optional[str] = None) -> Dict[str, Any]:
    """Load sealed seed JSON. Cached by absolute path string."""
    seed_path = Path(path) if path else DEFAULT_SEED_PATH
    if not seed_path.is_file():
        raise FileNotFoundError(f"Synth catalog seed not found: {seed_path}")
    return json.loads(seed_path.read_text(encoding="utf-8"))


def get_catalog_modules(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lightweight catalog rows (brand/name/hp/category/availability)."""
    seed = load_seed(str(Path(path).resolve()) if path else None)
    return list(seed.get("catalog_modules") or [])


def get_full_spec_modules(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Full Module table rows when present; fall back to curated constant."""
    try:
        seed = load_seed(str(Path(path).resolve()) if path else None)
        full = seed.get("full_spec_modules")
        if full:
            return list(full)
    except FileNotFoundError:
        pass
    return list(SYNTH_CATALOG_MODULES)


def get_brand_index(path: Optional[str] = None) -> List[str]:
    """767-brand index from research Phase 1."""
    seed = load_seed(str(Path(path).resolve()) if path else None)
    brands = seed.get("brands") or []
    return list(brands)


def get_major_brands(path: Optional[str] = None) -> List[str]:
    try:
        seed = load_seed(str(Path(path).resolve()) if path else None)
        major = seed.get("major_brands")
        if major:
            return list(major)
    except FileNotFoundError:
        pass
    return list(MAJOR_BRANDS)


def seed_stats(path: Optional[str] = None) -> Dict[str, Any]:
    seed = load_seed(str(Path(path).resolve()) if path else None)
    catalog = seed.get("catalog_modules") or []
    return {
        "fixture_version": seed.get("fixture_version"),
        "name": seed.get("name"),
        "generated_at": seed.get("generated_at"),
        "brand_count": seed.get("brand_count") or len(seed.get("brands") or []),
        "catalog_module_count": len(catalog),
        "full_spec_module_count": len(seed.get("full_spec_modules") or SYNTH_CATALOG_MODULES),
        "hp_known_count": sum(1 for m in catalog if m.get("hp") is not None),
        "content_hashes": seed.get("content_hashes"),
        "abraxas_pr": seed.get("abraxas_pr"),
        "seed_path": str(DEFAULT_SEED_PATH if not path else Path(path).resolve()),
    }
