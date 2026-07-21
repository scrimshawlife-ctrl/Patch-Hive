"""Unit tests for legacy run export bridge id/hash helpers."""

from runs.bridge import (
    legacy_artifact_manifest_hash,
    legacy_rig_revision_id,
    legacy_source_run_id,
)


def test_legacy_bridge_ids_are_stable() -> None:
    assert legacy_rig_revision_id(42) == "legacy-rack-42"
    assert legacy_source_run_id(7) == "legacy-run-7"
    h1 = legacy_artifact_manifest_hash(7, 42)
    h2 = legacy_artifact_manifest_hash(7, 42)
    assert h1 == h2
    assert len(h1) == 64
    assert h1 != legacy_artifact_manifest_hash(8, 42)
