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
    operations: List["RuneOperation"]


@dataclass(frozen=True)
class RuneOperation:
    rune_id: str
    name: str
    maps_to: str
    input_schema: str
    output_schema: str
    version: str
    determinism_class: str
    permitted_side_effects: List[str]
    authority_requirement: str
    failure_taxonomy: List[str]
    test_vectors: List[str]


def parse_manifest(data: Dict[str, Any]) -> RuneManifest:
    for key in ("schema_version", "engine_version", "runes", "operations"):
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

    operations = []
    operation_keys = (
        "rune_id",
        "name",
        "maps_to",
        "input_schema",
        "output_schema",
        "version",
        "determinism_class",
        "permitted_side_effects",
        "authority_requirement",
        "failure_taxonomy",
        "test_vectors",
    )
    for entry in data["operations"]:
        for key in operation_keys:
            if key not in entry:
                raise ValueError(f"Missing rune operation key: {key}")
        operations.append(
            RuneOperation(
                rune_id=str(entry["rune_id"]),
                name=str(entry["name"]),
                maps_to=str(entry["maps_to"]),
                input_schema=str(entry["input_schema"]),
                output_schema=str(entry["output_schema"]),
                version=str(entry["version"]),
                determinism_class=str(entry["determinism_class"]),
                permitted_side_effects=list(entry["permitted_side_effects"]),
                authority_requirement=str(entry["authority_requirement"]),
                failure_taxonomy=list(entry["failure_taxonomy"]),
                test_vectors=list(entry["test_vectors"]),
            )
        )

    return RuneManifest(
        schema_version=str(data["schema_version"]),
        engine_version=str(data["engine_version"]),
        runes=runes,
        operations=operations,
    )
