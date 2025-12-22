from __future__ import annotations

import json
from pathlib import Path
from patchhive.cli.ingest_modulargrid_dataset import (
    ingest_modulargrid_dataset,
    stable_module_id,
    stable_module_key,
    slugify,
    gen_panel_svg,
)
from patchhive.gallery.store_v2 import ModuleGalleryStoreV2


def test_slugify():
    """Test slugify function."""
    assert slugify("Mutable Instruments") == "mutable-instruments"
    assert slugify("VCA/Mixer") == "vca-mixer"
    assert slugify("  Voltage Lab 2  ") == "voltage-lab-2"
    assert slugify("LPG (Low Pass Gate)") == "lpg-low-pass-gate"
    assert slugify("") == "unnamed"


def test_stable_module_key():
    """Test stable module key generation."""
    key1 = stable_module_key("Mutable Instruments", "Plaits", 12)
    assert key1 == "mutable-instruments__plaits__12hp"

    key2 = stable_module_key("Make Noise", "Maths", 20)
    assert key2 == "make-noise__maths__20hp"

    # Same inputs should produce same key
    key3 = stable_module_key("Mutable Instruments", "Plaits", 12)
    assert key1 == key3


def test_gen_panel_svg():
    """Test SVG panel generation."""
    svg = gen_panel_svg(
        title="Plaits",
        manufacturer="Mutable Instruments",
        hp=12,
        jacks=[],
    )
    assert "<?xml version" in svg
    assert "Plaits" in svg
    assert "Mutable Instruments" in svg
    assert "12 HP" in svg
    assert "JACKS: TBD" in svg

    # With jacks
    svg2 = gen_panel_svg(
        title="VCA",
        manufacturer="Test",
        hp=8,
        jacks=[("IN", "in"), ("OUT", "out"), ("CV", "cv")],
    )
    assert "JACKS: TBD" not in svg2
    assert "IN" in svg2
    assert "OUT" in svg2
    assert "CV" in svg2


def test_ingest_modulargrid_dataset(tmp_path: Path):
    """Test full ModularGrid dataset ingestion."""
    # Create test dataset
    dataset = {
        "metadata": {
            "source": "ModularGrid Top 100",
            "database_version": "2024-01-01",
        },
        "modules": [
            {
                "manufacturer": "Mutable Instruments",
                "module_name": "Plaits",
                "hp_width": 12,
                "depth_mm": 25,
                "primary_function": "Oscillator",
                "secondary_functions": "Wavetable, FM, Physical Modeling",
            },
            {
                "manufacturer": "Make Noise",
                "module_name": "Maths",
                "hp_width": 20,
                "depth_mm": 26,
                "primary_function": "Function Generator",
                "secondary_functions": "Envelope, LFO, Slew",
            },
            {
                "manufacturer": "Invalid",
                "module_name": "",  # Should be skipped
            },
        ],
    }

    src_json = tmp_path / "test_dataset.json"
    src_json.write_text(json.dumps(dataset), encoding="utf-8")

    gallery_root = str(tmp_path / "gallery")

    # Run ingestion
    manifest = ingest_modulargrid_dataset(
        src_json,
        gallery_root,
        source_name="Test Source",
        database_version="test-v1",
    )

    # Verify manifest
    assert manifest["kind"] == "patchhive.ingest_manifest"
    assert manifest["source"] == "ModularGrid Top 100"
    assert manifest["database_version"] == "2024-01-01"
    assert manifest["modules_ingested"] == 2
    assert manifest["modules_skipped"] == 1
    assert "module_library_root" in manifest
    assert "gallery_entries_root" in manifest

    # Verify gallery store
    store = ModuleGalleryStoreV2(gallery_root)

    # Check Plaits
    plaits_key = stable_module_key("Mutable Instruments", "Plaits", 12)
    plaits_rev = store.read_latest(plaits_key)
    assert plaits_rev is not None
    assert plaits_rev.identity.manufacturer == "Mutable Instruments"
    assert plaits_rev.identity.name == "Plaits"
    assert plaits_rev.identity.hp == 12
    assert plaits_rev.jacks == []  # Empty until discovered
    assert len(plaits_rev.attachments) == 1
    assert plaits_rev.attachments[0].type.value == "sketch_svg"
    assert "Oscillator" in plaits_rev.tags
    assert "Wavetable" in plaits_rev.tags

    # Check Maths
    maths_key = stable_module_key("Make Noise", "Maths", 20)
    maths_rev = store.read_latest(maths_key)
    assert maths_rev is not None
    assert maths_rev.identity.manufacturer == "Make Noise"
    assert maths_rev.identity.name == "Maths"
    assert maths_rev.identity.hp == 20
    assert "Function Generator" in maths_rev.tags
    assert "Envelope" in maths_rev.tags

    # Verify manifest file was written
    manifest_path = Path(gallery_root) / "ingest_manifest.json"
    assert manifest_path.exists()
    saved_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved_manifest["modules_ingested"] == 2

    # Verify module library entry + gallery entry JSON
    module_id = stable_module_id("Mutable Instruments", "Plaits")
    library_entry = json.loads(
        (Path(manifest["module_library_root"]) / f"{module_id}.json").read_text(encoding="utf-8")
    )
    assert library_entry["module_id"] == module_id
    assert library_entry["manufacturer"] == "Mutable Instruments"
    assert library_entry["module_name"] == "Plaits"
    assert library_entry["physical"]["hp"] == 12
    assert library_entry["physical"]["depth_mm"] == 25
    assert library_entry["jacks"] == []

    gallery_entry = json.loads(
        (Path(manifest["gallery_entries_root"]) / f"{module_id}.json").read_text(encoding="utf-8")
    )
    assert gallery_entry["module_id"] == module_id
    assert gallery_entry["panel_image"] is None
    assert "JACKS: TBD" in gallery_entry["panel_sketch"]


def test_ingest_idempotency(tmp_path: Path):
    """Test that ingestion is idempotent (skips existing modules)."""
    dataset = {
        "metadata": {"source": "Test", "database_version": "v1"},
        "modules": [
            {
                "manufacturer": "Test Mfr",
                "module_name": "Test Module",
                "hp_width": 8,
                "primary_function": "Utility",
            },
        ],
    }

    src_json = tmp_path / "test.json"
    src_json.write_text(json.dumps(dataset), encoding="utf-8")

    gallery_root = str(tmp_path / "gallery")

    # First ingestion
    manifest1 = ingest_modulargrid_dataset(src_json, gallery_root)
    assert manifest1["modules_ingested"] == 1
    assert manifest1["modules_skipped"] == 0

    # Second ingestion (should skip existing)
    manifest2 = ingest_modulargrid_dataset(src_json, gallery_root)
    assert manifest2["modules_ingested"] == 0
    assert manifest2["modules_skipped"] == 1

    # Verify only one revision exists
    store = ModuleGalleryStoreV2(gallery_root)
    module_key = stable_module_key("Test Mfr", "Test Module", 8)
    revisions = store.read_all_revisions(module_key)
    assert len(revisions) == 1
