"""
ModularGrid import adapter (boundary only).
This module provides an interface for importing module data from ModularGrid.

Implementation lives outside core PatchHive and must be injected explicitly.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from modules.models import Module


class ModularGridAdapter:
    """Adapter for importing data from ModularGrid."""

    def __init__(self, db: Session):
        self.db = db

    def import_from_url(self, url: str) -> List[Module]:
        """
        Import modules from a ModularGrid URL.

        Args:
            url: ModularGrid rack or module URL

        Returns:
            List of imported Module objects

        """
        raise ModularGridUnavailableError(
            "ModularGrid import adapter is unavailable. "
            "Provide an external implementation via dependency injection."
        )

    def import_from_id(self, modulargrid_id: str) -> Optional[Module]:
        """
        Import a single module by ModularGrid ID.

        Args:
            modulargrid_id: ModularGrid module ID

        Returns:
            Imported Module object or None

        """
        raise ModularGridUnavailableError(
            "ModularGrid import adapter is unavailable. "
            "Provide an external implementation via dependency injection."
        )

    def search_modules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search ModularGrid for modules.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of module metadata dictionaries

        """
        raise ModularGridUnavailableError(
            "ModularGrid search adapter is unavailable. "
            "Provide an external implementation via dependency injection."
        )


def create_modulargrid_adapter(db: Session) -> ModularGridAdapter:
    """Factory function to create ModularGrid adapter."""
    return ModularGridAdapter(db)


class ModularGridUnavailableError(RuntimeError):
    """Raised when the ModularGrid adapter is not configured."""
