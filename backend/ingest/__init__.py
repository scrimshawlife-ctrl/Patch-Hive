"""Ingest domain - Data import from external sources."""
from .modulargrid import create_modulargrid_adapter, ModularGridAdapter

__all__ = ["create_modulargrid_adapter", "ModularGridAdapter"]
