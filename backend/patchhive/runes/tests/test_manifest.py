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
