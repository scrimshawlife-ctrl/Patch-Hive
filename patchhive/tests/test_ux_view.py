from __future__ import annotations

import json
from pathlib import Path
from patchhive.ops.build_ux_view import build_ux_view


def test_build_ux_view(tmp_path: Path):
    """Test that UX view builds correctly from library and manifest."""
    (tmp_path / "svgs").mkdir()
    (tmp_path / "pdf").mkdir()
    (tmp_path / "json").mkdir()

    (tmp_path / "json" / "library.json").write_text(json.dumps({
        "patches": [
            {"card": {"patch_id": "p1", "name": "Voice Enveloped Filtered Mk.AAAA", "category": "Voice",
                      "difficulty": "Beginner", "cable_count": 4, "stability_score": 0.9, "warnings": [], "tags": []},
             "patch": {"patch_id": "p1", "cables": []}}
        ]
    }), encoding="utf-8")

    (tmp_path / "manifest.json").write_text(json.dumps({
        "rig_id": "rig.test",
        "stats": {"categories": {"Voice": 1}, "difficulty": {"Beginner": 1}}
    }), encoding="utf-8")

    ux = build_ux_view(run_root=str(tmp_path), run_id="run1")
    assert ux.patch_count == 1
    assert ux.items[0].svg_path == "svgs/p1.svg"
    assert ux.rig_id == "rig.test"
    assert ux.run_id == "run1"
    assert ux.categories["Voice"] == 1
    assert ux.difficulty["Beginner"] == 1


def test_build_ux_view_without_stats(tmp_path: Path):
    """Test that UX view computes stats when not provided in manifest."""
    (tmp_path / "json").mkdir()

    (tmp_path / "json" / "library.json").write_text(json.dumps({
        "patches": [
            {"card": {"patch_id": "p1", "name": "Patch 1", "category": "Voice",
                      "difficulty": "Beginner", "cable_count": 4, "stability_score": 0.9}},
            {"card": {"patch_id": "p2", "name": "Patch 2", "category": "Generative",
                      "difficulty": "Advanced", "cable_count": 8, "stability_score": 0.7}},
        ]
    }), encoding="utf-8")

    (tmp_path / "manifest.json").write_text(json.dumps({
        "rig_id": "rig.test2",
    }), encoding="utf-8")

    ux = build_ux_view(run_root=str(tmp_path), run_id="run2")
    assert ux.patch_count == 2
    assert ux.categories["Voice"] == 1
    assert ux.categories["Generative"] == 1
    assert ux.difficulty["Beginner"] == 1
    assert ux.difficulty["Advanced"] == 1


def test_build_ux_view_sorted(tmp_path: Path):
    """Test that items are sorted by category, difficulty, name."""
    (tmp_path / "json").mkdir()

    (tmp_path / "json" / "library.json").write_text(json.dumps({
        "patches": [
            {"card": {"patch_id": "p3", "name": "Z Patch", "category": "Voice",
                      "difficulty": "Advanced", "cable_count": 4, "stability_score": 0.9}},
            {"card": {"patch_id": "p1", "name": "A Patch", "category": "Voice",
                      "difficulty": "Beginner", "cable_count": 4, "stability_score": 0.9}},
            {"card": {"patch_id": "p2", "name": "M Patch", "category": "Generative",
                      "difficulty": "Beginner", "cable_count": 8, "stability_score": 0.7}},
        ]
    }), encoding="utf-8")

    (tmp_path / "manifest.json").write_text(json.dumps({"rig_id": "rig.test3"}), encoding="utf-8")

    ux = build_ux_view(run_root=str(tmp_path), run_id="run3")
    assert ux.patch_count == 3
    # Should be sorted by category (alphabetical), then difficulty (alphabetical), then name
    # Order: Generative/Beginner, Voice/Advanced (A<B), Voice/Beginner
    assert ux.items[0].category == "Generative"
    assert ux.items[0].difficulty == "Beginner"
    assert ux.items[0].name == "M Patch"
    assert ux.items[1].category == "Voice"
    assert ux.items[1].difficulty == "Advanced"  # Advanced < Beginner alphabetically
    assert ux.items[1].name == "Z Patch"
    assert ux.items[2].category == "Voice"
    assert ux.items[2].difficulty == "Beginner"
    assert ux.items[2].name == "A Patch"
