"""
System Packs Loader

Loads reference patches from the system_packs/ directory.
System packs provide validated, canonical patch definitions for various synthesizer systems.
"""
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SystemPackPatch:
    """Represents a patch from a system pack."""
    id: str
    name: str
    system: str
    schema_version: str
    intent: str
    tags: List[str]
    modules: Dict[str, Any]
    wiring: List[Dict[str, Any]]
    notes: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class SystemPack:
    """Represents a system pack with metadata and patches."""
    name: str
    system: str
    version: str
    schema_version: str
    description: str
    patches: List[SystemPackPatch]
    schema_file: str
    ontology: Dict[str, str]


class SystemPackLoader:
    """Loads and manages system packs from the filesystem."""

    def __init__(self, packs_root: Optional[Path] = None):
        """
        Initialize the loader.

        Args:
            packs_root: Root directory containing system packs.
                       Defaults to ../../system_packs relative to this file.
        """
        if packs_root is None:
            # Default to system_packs in repo root
            backend_dir = Path(__file__).parent.parent
            repo_root = backend_dir.parent
            packs_root = repo_root / "system_packs"

        self.packs_root = Path(packs_root)
        self._packs_cache: Dict[str, SystemPack] = {}

    def list_available_packs(self) -> List[str]:
        """
        List all available system pack names.

        Returns:
            List of system pack directory names
        """
        if not self.packs_root.exists():
            return []

        return [
            d.name for d in self.packs_root.iterdir()
            if d.is_dir() and (d / "pack.manifest.json").exists()
        ]

    def load_pack(self, pack_name: str) -> SystemPack:
        """
        Load a system pack by name.

        Args:
            pack_name: Name of the pack directory (e.g., 'vl2')

        Returns:
            SystemPack object with all patches loaded

        Raises:
            FileNotFoundError: If pack doesn't exist
            ValueError: If manifest is invalid
        """
        # Check cache
        if pack_name in self._packs_cache:
            return self._packs_cache[pack_name]

        pack_dir = self.packs_root / pack_name
        if not pack_dir.exists():
            raise FileNotFoundError(f"System pack '{pack_name}' not found at {pack_dir}")

        # Load manifest
        manifest_path = pack_dir / "pack.manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Load patches
        patches = []
        for patch_entry in manifest.get("patches", []):
            patch_file = pack_dir / patch_entry["file"]
            if not patch_file.exists():
                raise FileNotFoundError(f"Patch file not found: {patch_file}")

            with open(patch_file, 'r') as f:
                patch_data = yaml.safe_load(f)

            patch = SystemPackPatch(
                id=patch_data["id"],
                name=patch_data["name"],
                system=patch_data["system"],
                schema_version=patch_data["schemaVersion"],
                intent=patch_data.get("intent", ""),
                tags=patch_data.get("tags", []),
                modules=patch_data.get("modules", {}),
                wiring=patch_data.get("wiring", []),
                notes=patch_data.get("notes"),
                file_path=str(patch_file)
            )
            patches.append(patch)

        # Create pack object
        pack = SystemPack(
            name=manifest["name"],
            system=manifest["system"],
            version=manifest["version"],
            schema_version=manifest["schemaVersion"],
            description=manifest["description"],
            patches=patches,
            schema_file=str(pack_dir / manifest["schema"]["file"]),
            ontology=manifest.get("ontology", {})
        )

        # Cache and return
        self._packs_cache[pack_name] = pack
        return pack

    def get_patch_by_id(self, pack_name: str, patch_id: str) -> Optional[SystemPackPatch]:
        """
        Get a specific patch by ID from a pack.

        Args:
            pack_name: Name of the system pack
            patch_id: Patch identifier (e.g., 'PHVL2-0001')

        Returns:
            SystemPackPatch object or None if not found
        """
        pack = self.load_pack(pack_name)
        for patch in pack.patches:
            if patch.id == patch_id:
                return patch
        return None

    def search_patches(
        self,
        pack_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        system: Optional[str] = None
    ) -> List[SystemPackPatch]:
        """
        Search for patches across packs.

        Args:
            pack_name: Optional pack name to filter by
            tags: Optional list of tags to filter by (any match)
            system: Optional system name to filter by

        Returns:
            List of matching patches
        """
        results = []

        # Determine which packs to search
        if pack_name:
            packs_to_search = [pack_name]
        else:
            packs_to_search = self.list_available_packs()

        # Search each pack
        for pack in packs_to_search:
            try:
                loaded_pack = self.load_pack(pack)

                for patch in loaded_pack.patches:
                    # Filter by system
                    if system and patch.system != system:
                        continue

                    # Filter by tags
                    if tags and not any(tag in patch.tags for tag in tags):
                        continue

                    results.append(patch)
            except (FileNotFoundError, ValueError):
                # Skip packs that fail to load
                continue

        return results

    def validate_pack(self, pack_name: str) -> Dict[str, Any]:
        """
        Validate a system pack's integrity.

        Args:
            pack_name: Name of the pack to validate

        Returns:
            Dictionary with validation results
        """
        try:
            pack = self.load_pack(pack_name)

            return {
                "valid": True,
                "pack_name": pack_name,
                "system": pack.system,
                "patches_loaded": len(pack.patches),
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "pack_name": pack_name,
                "errors": [str(e)]
            }


# Factory function for dependency injection
def create_system_pack_loader(packs_root: Optional[Path] = None) -> SystemPackLoader:
    """Create a SystemPackLoader instance."""
    return SystemPackLoader(packs_root)
