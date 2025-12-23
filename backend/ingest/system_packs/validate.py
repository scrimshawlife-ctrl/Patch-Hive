"""
Validation utilities for system packs.
Provides SHA-256 verification and structure validation.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any

import yaml
from pydantic import ValidationError

from .models import SystemPackManifest, VL2Patch


def sha256_file(path: Path) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        path: Path to file

    Returns:
        Hex string of SHA-256 hash
    """
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(path: Path) -> dict:
    """
    Load JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If JSON is invalid
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")


def load_yaml(path: Path) -> dict:
    """
    Load YAML file using safe loader.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML dictionary

    Raises:
        ValueError: If YAML is invalid
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}")
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")


def validate_manifest(manifest: SystemPackManifest) -> None:
    """
    Validate system pack manifest structure.

    Args:
        manifest: Parsed manifest object

    Raises:
        ValueError: If manifest is invalid
    """
    if not manifest.patches:
        raise ValueError("Manifest must contain at least one patch")

    if not manifest.system:
        raise ValueError("Manifest must specify system")

    if not manifest.schemaVersion:
        raise ValueError("Manifest must specify schemaVersion")

    # Check for duplicate patch IDs
    patch_ids = [p.id for p in manifest.patches]
    if len(patch_ids) != len(set(patch_ids)):
        duplicates = [pid for pid in patch_ids if patch_ids.count(pid) > 1]
        raise ValueError(f"Duplicate patch IDs found: {set(duplicates)}")


def validate_hashes(pack_dir: Path, manifest: SystemPackManifest) -> None:
    """
    Validate SHA-256 hashes for all patch files.

    Args:
        pack_dir: Root directory of the system pack
        manifest: Loaded manifest

    Raises:
        ValueError: If any hash mismatch is found
    """
    errors = []

    for patch_ref in sorted(manifest.patches, key=lambda p: p.id):
        patch_path = pack_dir / patch_ref.file
        if not patch_path.exists():
            errors.append(f"{patch_ref.id}: File not found at {patch_path}")
            continue

        computed_hash = sha256_file(patch_path)
        if computed_hash != patch_ref.sha256:
            errors.append(
                f"{patch_ref.id}: Hash mismatch\n"
                f"  Expected: {patch_ref.sha256}\n"
                f"  Got:      {computed_hash}"
            )

    if errors:
        raise ValueError("Hash validation failed:\n" + "\n".join(errors))


def validate_patches(patch_dicts: List[dict]) -> List[VL2Patch]:
    """
    Validate patch dictionaries using Pydantic models.

    Args:
        patch_dicts: List of raw patch dictionaries

    Returns:
        List of validated VL2Patch objects

    Raises:
        ValueError: If any patch fails validation
    """
    validated_patches = []
    errors = []

    for patch_dict in patch_dicts:
        patch_id = patch_dict.get("id", "unknown")
        try:
            patch = VL2Patch(**patch_dict)
            validated_patches.append(patch)
        except ValidationError as e:
            errors.append(f"{patch_id}: Validation failed:\n{e}")

    if errors:
        raise ValueError("Patch validation failed:\n" + "\n".join(errors))

    return validated_patches
