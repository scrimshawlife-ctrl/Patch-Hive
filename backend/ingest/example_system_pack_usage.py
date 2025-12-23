#!/usr/bin/env python3
"""
Example usage of the SystemPackLoader.

This script demonstrates how to load and query system packs.
"""
from system_packs import create_system_pack_loader


def main():
    # Create loader
    loader = create_system_pack_loader()

    # List available packs
    print("Available system packs:")
    packs = loader.list_available_packs()
    for pack_name in packs:
        print(f"  - {pack_name}")
    print()

    # Load the VL2 pack
    if "vl2" in packs:
        print("Loading VL2 pack...")
        vl2_pack = loader.load_pack("vl2")

        print(f"Pack: {vl2_pack.name}")
        print(f"System: {vl2_pack.system}")
        print(f"Version: {vl2_pack.version}")
        print(f"Schema: {vl2_pack.schema_version}")
        print(f"Description: {vl2_pack.description}")
        print(f"Total patches: {len(vl2_pack.patches)}")
        print()

        # List all patches
        print("Patches:")
        for patch in vl2_pack.patches:
            print(f"  {patch.id}: {patch.name}")
            print(f"    Tags: {', '.join(patch.tags)}")
            print(f"    Intent: {patch.intent}")
            print()

        # Search for probabilistic patches
        print("Searching for probabilistic patches:")
        probabilistic = loader.search_patches(pack_name="vl2", tags=["probabilistic"])
        for patch in probabilistic:
            print(f"  {patch.id}: {patch.name}")
        print()

        # Get specific patch
        print("Loading PHVL2-0001:")
        patch = loader.get_patch_by_id("vl2", "PHVL2-0001")
        if patch:
            print(f"  Name: {patch.name}")
            print(f"  Wiring connections: {len(patch.wiring)}")
            print(f"  Modules configured:")
            for module_type, config in patch.modules.items():
                if config:
                    print(f"    - {module_type}: {list(config.keys())}")
        print()

        # Validate pack
        print("Validating pack...")
        result = loader.validate_pack("vl2")
        print(f"  Valid: {result['valid']}")
        print(f"  Patches loaded: {result.get('patches_loaded', 0)}")
        if result.get('errors'):
            print(f"  Errors: {result['errors']}")


if __name__ == "__main__":
    main()
