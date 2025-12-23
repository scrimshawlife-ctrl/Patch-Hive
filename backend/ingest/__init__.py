"""Ingest domain - Data import from external sources."""

__all__ = [
    "create_modulargrid_adapter",
    "ModularGridAdapter",
    "SystemPackManifest",
    "SystemPackLoaded",
    "PatchRef",
    "import_system_pack",
]


def __getattr__(name):
    """Lazy imports to avoid circular dependencies."""
    if name in ("create_modulargrid_adapter", "ModularGridAdapter"):
        from .modulargrid import create_modulargrid_adapter, ModularGridAdapter

        globals()["create_modulargrid_adapter"] = create_modulargrid_adapter
        globals()["ModularGridAdapter"] = ModularGridAdapter
        return globals()[name]
    elif name in (
        "SystemPackManifest",
        "SystemPackLoaded",
        "PatchRef",
        "import_system_pack",
    ):
        from .system_packs import (
            SystemPackManifest,
            SystemPackLoaded,
            PatchRef,
            import_system_pack,
        )

        globals()["SystemPackManifest"] = SystemPackManifest
        globals()["SystemPackLoaded"] = SystemPackLoaded
        globals()["PatchRef"] = PatchRef
        globals()["import_system_pack"] = import_system_pack
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
