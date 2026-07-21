#!/usr/bin/env python3
"""Build Phase 3 mid-tier condensed module seed from research markdown.

Parses ``- **ModuleName** – description`` bullets under brand headings.
HP remains null unless the description explicitly states N HP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO / "data" / "synth-catalog" / "phase3-mid-tier.md"
DEFAULT_OUT = REPO / "data" / "synth-catalog" / "seed-phase3-v1.json"

# Copy from Abraxas if present
ABX_PHASE3 = (
    Path.home()
    / "Documents"
    / "Abraxas-v2.0"
    / "skills"
    / "modular-synth-catalog-research"
    / "references"
    / "phase3-mid-tier.md"
)


def map_category_from_desc(text: str) -> str:
    r = (text or "").lower()
    rules = [
        (("oscillator", "vco", "voice", "semi-modular"), "VCO"),
        (("filter", "vcf"), "VCF"),
        (("vca",), "VCA"),
        (("envelope", "eg"), "ENV"),
        (("lfo",), "LFO"),
        (("sequencer", "clock"), "SEQ"),
        (("delay", "reverb", "effect", "looper", "tape"), "FX"),
        (("mixer", "mix"), "MIX"),
        (("granular", "sample", "sampler"), "SAMP"),
        (("midi",), "MIDI"),
    ]
    for keys, cat in rules:
        if any(k in r for k in keys):
            return cat
    return "UTIL"


def parse_hp_from_desc(text: str):
    m = re.search(r"\b(\d{1,2})\s*HP\b", text or "", re.I)
    return int(m.group(1)) if m else None


def parse_phase3(text: str) -> list[dict]:
    modules: list[dict] = []
    current_brand = None
    seen: set[tuple[str, str]] = set()

    for line in text.splitlines():
        # ## Instruō (Glasgow, Scotland) – Condensed
        m_h = re.match(r"^##\s+(.+?)(?:\s*[–—(-].*)?$", line.strip())
        if m_h and not line.strip().startswith("###"):
            brand = m_h.group(1).strip()
            # skip non-brand section headers
            if brand.lower().startswith(("phase", "campaign", "autonomous", "in progress")):
                continue
            # normalize unicode brand spellings for catalog join
            brand = brand.replace("Instruō", "Instruo").replace("Instruó", "Instruo")
            current_brand = brand
            continue

        # - **arbhar** – Granular processor
        m_mod = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*[–—:-]\s*(.+)$", line)
        if not current_brand or not m_mod:
            continue
        name = m_mod.group(1).strip()
        desc = m_mod.group(2).strip()
        if not name or name.lower() in {"status", "website", "specialty", "summary"}:
            continue
        key = (current_brand.lower(), name.lower())
        if key in seen:
            continue
        seen.add(key)
        modules.append(
            {
                "brand": current_brand,
                "name": name,
                "hp": parse_hp_from_desc(desc),
                "category": map_category_from_desc(desc),
                "category_raw": desc,
                "is_available": "available",
                "description": desc,
                "source": "SynthCatalogResearch",
                "source_reference": "data/synth-catalog/seed-phase3-v1.json",
                "provenance": "OBSERVED",
                "research_phase": "phase3",
            }
        )

    modules.sort(key=lambda m: (m["brand"].lower(), m["name"].lower()))
    return modules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    source = args.source
    if source is None:
        if ABX_PHASE3.is_file():
            source = ABX_PHASE3
        elif DEFAULT_SOURCE.is_file():
            source = DEFAULT_SOURCE
        else:
            print("error: phase3 markdown not found")
            return 1

    text = source.read_text(encoding="utf-8")
    # Keep audit copy under data/synth-catalog
    audit = REPO / "data" / "synth-catalog" / "phase3-mid-tier.md"
    audit.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != audit.resolve():
        audit.write_text(text, encoding="utf-8")

    modules = parse_phase3(text)
    payload = {
        "fixture_version": "1.0",
        "name": "Synth Catalog Research — Phase 3 mid-tier condensed seed",
        "generated_at": "2026-07-21T00:00:00Z",
        "source_note": (
            "Condensed mid-tier brand key-modules from research Phase 3. "
            "HP null unless description explicitly states width. Never invent."
        ),
        "abraxas_skill": "skills/modular-synth-catalog-research",
        "research_phase": "phase3",
        "content_hashes": {
            "phase3_mid_tier_sha256": hashlib.sha256(text.encode()).hexdigest(),
        },
        "catalog_module_count": len(modules),
        "catalog_modules": modules,
        "full_spec_modules": [],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    backend_pack = REPO / "backend" / "data" / "synth-catalog"
    backend_pack.mkdir(parents=True, exist_ok=True)
    # phase3 is separate seed file; importer can load via --seed
    (backend_pack / "seed-phase3-v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "status": "success",
                "source": str(source),
                "out": str(args.out),
                "modules": len(modules),
                "hp_known": sum(1 for m in modules if m.get("hp") is not None),
                "brands": sorted({m["brand"] for m in modules}),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
