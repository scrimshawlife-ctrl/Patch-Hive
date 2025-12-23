"""
System Pack Importer

Loads and validates system packs from the filesystem.
By default, operates in read-only mode (persist=False).
"""
from pathlib import Path
from typing import Optional

from .models import SystemPackManifest, SystemPackLoaded, OntologyData
from .validate import (
    load_json,
    load_yaml,
    validate_manifest,
    validate_hashes,
    validate_patches,
)


def import_system_pack(pack_dir: str, *, persist: bool = False) -> SystemPackLoaded:
    """
    Import a system pack from the filesystem.

    Args:
        pack_dir: Path to system pack directory (e.g., "system_packs/vl2")
        persist: If True, save to database (TODO: not yet implemented)

    Returns:
        SystemPackLoaded object with all patches and ontology data

    Raises:
        ValueError: If pack is invalid or fails validation
        FileNotFoundError: If pack directory or required files not found

    Example:
        >>> pack = import_system_pack("system_packs/vl2")
        >>> print(f"Loaded {pack.patch_count} patches for {pack.system_id}")
    """
    # Resolve pack directory
    pack_path = Path(pack_dir).resolve()
    if not pack_path.exists():
        raise FileNotFoundError(f"System pack directory not found: {pack_path}")

    # Load manifest
    manifest_path = pack_path / "pack.manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest_dict = load_json(manifest_path)
    manifest = SystemPackManifest(**manifest_dict)

    # Validate manifest structure
    validate_manifest(manifest)

    # Verify SHA-256 hashes
    validate_hashes(pack_path, manifest)

    # Load ontology files (deterministic order)
    # Paths in manifest already include subdirectory (e.g., "ontology/roles.v1.json")
    roles_dict = load_json(pack_path / manifest.ontology.roles)
    operations_dict = load_json(pack_path / manifest.ontology.operations)
    tags_dict = load_json(pack_path / manifest.ontology.tags)

    ontology = OntologyData(
        roles=roles_dict, operations=operations_dict, tags=tags_dict
    )

    # Load patches (deterministic order by ID)
    patch_dicts = []
    for patch_ref in sorted(manifest.patches, key=lambda p: p.id):
        patch_path = pack_path / patch_ref.file
        patch_dict = load_yaml(patch_path)
        patch_dicts.append(patch_dict)

    # Validate patches via Pydantic
    patches = validate_patches(patch_dicts)

    # Construct loaded pack
    loaded = SystemPackLoaded(
        system_id=manifest.system,
        schema_version=manifest.schemaVersion,
        pack_version=manifest.version,
        description=manifest.description,
        ontology=ontology,
        patches=patches,
        patch_count=len(patches),
    )

    # TODO: Database persistence
    if persist:
        # Stub for DB persistence
        # Would integrate with existing patches.crud or new system_pack_crud module
        # Example pattern:
        #   from patches.crud import create_patch
        #   for patch in patches:
        #       create_patch(db, patch_data=patch)
        raise NotImplementedError(
            "Database persistence not yet implemented. "
            "To integrate with DB, implement in patches/crud.py "
            "following existing CRUD patterns for Patch model."
        )

    return loaded
