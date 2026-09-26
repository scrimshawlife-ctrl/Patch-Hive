"""Tests for the acquisition-to-review-queue promotion workbench."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "build_vision_promotion_queue.py"
SPEC = spec_from_file_location("build_vision_promotion_queue", SCRIPT)
assert SPEC and SPEC.loader
module = module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_only_rights_confirmed_assets_enter_queue_and_unknowns_stay_unknown():
    discovery = [
        {
            "record_id": "m1",
            "rights_status": "RIGHTS_CONFIRMED",
            "sha256": "a" * 64,
            "source_url": "https://example.invalid/a",
        },
        {
            "record_id": "m2",
            "rights_status": "RIGHTS_RESTRICTED",
            "sha256": "b" * 64,
            "source_url": "https://example.invalid/b",
        },
    ]
    modules = [{"record_id": "m1", "manufacturer": "Maker", "model": "Module"}]
    result = module.build_queue(discovery, modules)
    assert result["rights_cleared"] == 1
    assert result["admitted"] == 0
    item = result["items"][0]
    assert item["asset_hash"] == "sha256:" + "a" * 64
    assert item["ground_truth_status"] == "UNVERIFIED"
    assert item["annotation_status"] == "DISCOVERED"
    assert item["reviewer"] is None
    assert item["used_for_tuning"] is None
    assert result["thresholds"] == "NOT_COMPUTABLE"


def test_queue_is_deterministic():
    discovery = [{
        "record_id": "m1",
        "rights_status": "RIGHTS_CONFIRMED",
        "sha256": "a" * 64,
        "source_url": "https://example.invalid/a",
    }]
    modules = [{"record_id": "m1", "model": "Module"}]
    assert module.build_queue(discovery, modules) == module.build_queue(discovery, modules)
