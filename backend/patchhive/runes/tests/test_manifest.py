from __future__ import annotations

from patchhive.runes.registry import (
    iter_core_handlers,
    load_manifest,
    rune_id_for,
    validate_manifest,
)


def test_manifest_validates() -> None:
    errors = validate_manifest()
    assert errors == []


def test_rune_ids_are_deterministic() -> None:
    manifest = load_manifest()
    for rune in manifest.runes:
        assert rune.rune_id == rune_id_for(maps_to=rune.maps_to, name=rune.name)


def test_core_handlers_are_mapped() -> None:
    manifest = load_manifest()
    mapped = {rune.maps_to for rune in manifest.runes}
    for handler in iter_core_handlers():
        assert handler in mapped


def test_canonical_operations_have_complete_execution_contracts() -> None:
    manifest = load_manifest()
    assert len(manifest.operations) == 8
    for operation in manifest.operations:
        assert operation.input_schema.startswith("patchhive.canon.v1#")
        assert operation.output_schema.startswith("patchhive.canon.v1#")
        assert operation.version
        assert operation.authority_requirement
        assert operation.failure_taxonomy
        assert operation.test_vectors
