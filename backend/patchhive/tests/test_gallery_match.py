from datetime import datetime, timezone

from patchhive.gallery.match import exact_match, fuzzy_match
from patchhive.schemas import ModuleGalleryEntry, ProvenanceRecord


def _entry(module_id: str, manufacturer: str, name: str, hp: int) -> ModuleGalleryEntry:
    timestamp = datetime(2025, 12, 21, tzinfo=timezone.utc)
    return ModuleGalleryEntry(
        module_gallery_id=module_id,
        rev=timestamp,
        name=name,
        manufacturer=manufacturer,
        hp=hp,
        power=None,
        jacks=[],
        modes=None,
        images=[],
        sketch_svg=None,
        provenance=[
            ProvenanceRecord(
                type="manual",
                model_version=None,
                timestamp=timestamp,
                evidence_ref="test",
            )
        ],
        notes=[],
    )


def test_exact_match() -> None:
    entries = [
        _entry("mod.make_noise.maths", "Make Noise", "Maths", 20),
        _entry("mod.intellijel.plexus", "Intellijel", "Plexus", 12),
    ]
    match = exact_match(entries, manufacturer="Make Noise", name="Maths")
    assert match is not None
    assert match.module_gallery_id == "mod.make_noise.maths"


def test_fuzzy_match() -> None:
    entries = [
        _entry("mod.make_noise.maths", "Make Noise", "Maths", 20),
        _entry("mod.make_noise.morphagene", "Make Noise", "Morphagene", 20),
    ]
    candidate = fuzzy_match(
        entries, manufacturer="Make Noise", name="Math", hp_guess=20, min_score=0.5
    )
    assert candidate is not None
    assert candidate.module_gallery_id == "mod.make_noise.maths"
