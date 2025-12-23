"""
Tests for system pack import functionality.
"""
import json
import shutil
import tempfile
from pathlib import Path

import pytest

from ingest.system_packs import import_system_pack


def test_import_vl2_pack_succeeds():
    """Test that VL2 system pack imports successfully."""
    pack = import_system_pack("system_packs/vl2", persist=False)

    assert pack.system_id == "voltage-lab-2"
    assert pack.schema_version == "vl2.v1"
    assert pack.patch_count == 12
    assert len(pack.patches) == 12

    # Verify ontology loaded
    assert pack.ontology.roles is not None
    assert pack.ontology.operations is not None
    assert pack.ontology.tags is not None

    # Verify patches loaded correctly
    patch_ids = [p.id for p in pack.patches]
    assert "PHVL2-0001" in patch_ids
    assert "PHVL2-0012" in patch_ids

    # Verify patch structure
    first_patch = pack.patches[0]
    assert first_patch.id.startswith("PHVL2-")
    assert first_patch.name
    assert first_patch.system == "voltage-lab-2"
    assert first_patch.schemaVersion == "vl2.v1"
    assert first_patch.wiring  # Must have connections


def test_import_invalid_path_fails():
    """Test that importing nonexistent pack raises error."""
    with pytest.raises(FileNotFoundError, match="not found"):
        import_system_pack("system_packs/nonexistent", persist=False)


def test_import_hash_tamper_fails():
    """Test that hash validation detects tampered files."""
    # Create temporary pack copy
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path("system_packs/vl2")
        dst = Path(tmpdir) / "vl2_tampered"
        shutil.copytree(src, dst)

        # Tamper with a patch file
        patch_file = dst / "patches" / "PHVL2-0001.yaml"
        with open(patch_file, "a") as f:
            f.write("\n# tampered\n")

        # Should fail hash validation
        with pytest.raises(ValueError, match="Hash validation failed"):
            import_system_pack(str(dst), persist=False)


def test_import_missing_manifest_fails():
    """Test that missing manifest raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = Path(tmpdir) / "invalid_pack"
        pack_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            import_system_pack(str(pack_dir), persist=False)


def test_import_invalid_manifest_structure_fails():
    """Test that invalid manifest structure raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = Path(tmpdir) / "invalid_pack"
        pack_dir.mkdir()

        # Create invalid manifest (missing required fields)
        manifest = {
            "name": "Test Pack",
            # Missing required fields: system, version, schemaVersion, etc.
        }
        manifest_path = pack_dir / "pack.manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        with pytest.raises((ValueError, Exception)):
            import_system_pack(str(pack_dir), persist=False)


def test_patch_validation_structure():
    """Test that patches have expected structure."""
    pack = import_system_pack("system_packs/vl2", persist=False)

    for patch in pack.patches:
        # Required fields
        assert patch.id
        assert patch.name
        assert patch.system == "voltage-lab-2"
        assert patch.schemaVersion == "vl2.v1"

        # Modules configuration
        assert patch.modules
        assert isinstance(patch.modules, dict)

        # Wiring connections
        assert patch.wiring
        assert isinstance(patch.wiring, list)
        assert len(patch.wiring) > 0

        # Each connection must have required fields
        for conn in patch.wiring:
            assert conn.from_
            assert conn.to
            assert conn.type
            assert conn.role


def test_ontology_structure():
    """Test that ontology data is properly loaded."""
    pack = import_system_pack("system_packs/vl2", persist=False)

    # Roles ontology
    assert "roles" in pack.ontology.roles or "version" in pack.ontology.roles

    # Operations ontology
    assert (
        "operations" in pack.ontology.operations
        or "version" in pack.ontology.operations
    )

    # Tags ontology
    assert "allowedTags" in pack.ontology.tags or "version" in pack.ontology.tags


def test_patches_sorted_deterministically():
    """Test that patches are loaded in deterministic order."""
    pack1 = import_system_pack("system_packs/vl2", persist=False)
    pack2 = import_system_pack("system_packs/vl2", persist=False)

    ids1 = [p.id for p in pack1.patches]
    ids2 = [p.id for p in pack2.patches]

    # Should be identical order
    assert ids1 == ids2

    # Should be sorted
    assert ids1 == sorted(ids1)


def test_persist_flag_not_implemented():
    """Test that persist=True raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Database persistence"):
        import_system_pack("system_packs/vl2", persist=True)
