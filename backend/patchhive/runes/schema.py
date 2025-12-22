from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class RuneEntry:
    rune_id: str
    name: str
    category: str
    maps_to: str
    assets: List[str]
    provenance: Dict[str, Any]


@dataclass(frozen=True)
class RuneManifest:
    schema_version: str
    engine_version: str
    runes: List[RuneEntry]


def parse_manifest(data: Dict[str, Any]) -> RuneManifest:
    for key in ("schema_version", "engine_version", "runes"):
        if key not in data:
            raise ValueError(f"Missing manifest key: {key}")

    runes = []
    for entry in data["runes"]:
        for key in ("rune_id", "name", "category", "maps_to", "assets", "provenance"):
            if key not in entry:
                raise ValueError(f"Missing rune key: {key}")
        runes.append(
            RuneEntry(
                rune_id=str(entry["rune_id"]),
                name=str(entry["name"]),
                category=str(entry["category"]),
                maps_to=str(entry["maps_to"]),
                assets=list(entry["assets"]),
                provenance=dict(entry["provenance"]),
            )
        )

    return RuneManifest(
        schema_version=str(data["schema_version"]),
        engine_version=str(data["engine_version"]),
        runes=runes,
    )
