#!/usr/bin/env python3
"""
Standalone test for system pack import (no backend dependencies).
Run from repo root: python test_system_pack_standalone.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import only system_packs module (avoiding full backend imports)
from ingest.system_packs.importer import import_system_pack
from ingest.system_packs.validate import sha256_file

def test_vl2_import():
    """Test VL2 pack import."""
    print("Testing VL2 system pack import...")

    pack = import_system_pack("system_packs/vl2", persist=False)

    assert pack.system_id == "voltage-lab-2", f"Expected voltage-lab-2, got {pack.system_id}"
    assert pack.schema_version == "vl2.v1", f"Expected vl2.v1, got {pack.schema_version}"
    assert pack.patch_count == 12, f"Expected 12 patches, got {pack.patch_count}"
    assert len(pack.patches) == 12, f"Expected 12 patches in list, got {len(pack.patches)}"

    print(f"✅ Loaded {pack.patch_count} patches for {pack.system_id}")
    print(f"   Schema version: {pack.schema_version}")
    print(f"   Pack version: {pack.pack_version}")
    print(f"   Description: {pack.description}")

    # Check first patch structure
    first_patch = pack.patches[0]
    print(f"\n✅ First patch: {first_patch.id} - {first_patch.name}")
    print(f"   System: {first_patch.system}")
    print(f"   Wiring connections: {len(first_patch.wiring)}")
    print(f"   Tags: {', '.join(first_patch.tags or [])}")

    # Verify ontology
    print(f"\n✅ Ontology loaded:")
    print(f"   Roles: {len(pack.ontology.roles.get('roles', {}))}")
    print(f"   Operations: {len(pack.ontology.operations.get('operations', {}))}")
    print(f"   Tags: {len(pack.ontology.tags.get('allowedTags', []))}")

    # List all patches
    print(f"\n✅ All patches:")
    for patch in pack.patches:
        print(f"   {patch.id}: {patch.name}")

    print("\n✅ All tests passed!")
    return pack

if __name__ == "__main__":
    try:
        pack = test_vl2_import()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
