"""Build PatchBook document from database models."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule

from .branding import get_patchbook_branding
from .models import (
    IOEndpoint,
    ParameterSnapshot,
    PatchBookDocument,
    PatchBookHeader,
    PatchBookPage,
    PatchModulePosition,
)
from .patching_order import generate_patching_order
from .render_schematic import render_patch_schematic


def _build_module_inventory(rack_modules: list[RackModule], modules: dict[int, Module]) -> list[PatchModulePosition]:
    inventory = []
    for rack_module in rack_modules:
        module = modules.get(rack_module.module_id)
        if not module:
            continue
        inventory.append(
            PatchModulePosition(
                module_id=module.id,
                brand=module.brand,
                name=module.name,
                hp=module.hp,
                row_index=rack_module.row_index,
                start_hp=rack_module.start_hp,
            )
        )
    return inventory


def _build_io_inventory(connections: list[dict[str, Any]], modules: dict[int, Module]) -> list[IOEndpoint]:
    endpoints: list[IOEndpoint] = []
    for conn in connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        from_module = modules.get(from_id)
        to_module = modules.get(to_id)
        if from_module:
            endpoints.append(
                IOEndpoint(
                    module_id=from_module.id,
                    module_name=from_module.name,
                    port_name=conn.get("from_port", ""),
                    port_type=None,
                    direction="out",
                )
            )
        if to_module:
            endpoints.append(
                IOEndpoint(
                    module_id=to_module.id,
                    module_name=to_module.name,
                    port_name=conn.get("to_port", ""),
                    port_type=None,
                    direction="in",
                )
            )
    unique = {(e.module_id, e.port_name, e.direction): e for e in endpoints}
    return sorted(unique.values(), key=lambda e: (e.module_name, e.port_name, e.direction))


def _build_parameter_snapshot(patch: Patch, modules: dict[int, Module]) -> list[ParameterSnapshot]:
    snapshots: list[ParameterSnapshot] = []
    engine_config = patch.engine_config or {}
    parameters = engine_config.get("parameters") if isinstance(engine_config, dict) else None
    if isinstance(parameters, dict):
        for module_id_str, params in parameters.items():
            try:
                module_id = int(module_id_str)
            except (TypeError, ValueError):
                continue
            module = modules.get(module_id)
            if not module or not isinstance(params, dict):
                continue
            for param_name, value in sorted(params.items()):
                snapshots.append(
                    ParameterSnapshot(
                        module_id=module.id,
                        module_name=module.name,
                        parameter=param_name,
                        value=str(value),
                    )
                )
    return snapshots


def build_patchbook_document(
    db: Session,
    rack: Rack,
    patches: list[Patch],
    content_hash: str | None = None,
) -> PatchBookDocument:
    """Build PatchBook document from rack and patches."""
    rack_modules = (
        db.query(RackModule)
        .filter(RackModule.rack_id == rack.id)
        .order_by(RackModule.row_index.asc(), RackModule.start_hp.asc(), RackModule.module_id.asc())
        .all()
    )
    modules = {
        rack_module.module_id: db.query(Module).filter(Module.id == rack_module.module_id).first()
        for rack_module in rack_modules
    }
    modules = {module_id: module for module_id, module in modules.items() if module}

    pages: list[PatchBookPage] = []
    for patch in sorted(patches, key=lambda item: item.id):
        module_inventory = _build_module_inventory(rack_modules, modules)

        header = PatchBookHeader(
            title=patch.name,
            patch_id=patch.id,
            rack_id=rack.id,
            rack_name=rack.name,
        )
        io_inventory = _build_io_inventory(patch.connections, modules)
        parameter_snapshot = _build_parameter_snapshot(patch, modules)
        schematic = render_patch_schematic(db, rack, patch.connections)
        patching_order = generate_patching_order(patch.connections, modules)

        pages.append(
            PatchBookPage(
                header=header,
                module_inventory=module_inventory,
                io_inventory=io_inventory,
                parameter_snapshot=parameter_snapshot,
                schematic=schematic,
                patching_order=patching_order,
                variants=None,
            )
        )

    branding = get_patchbook_branding()
    return PatchBookDocument(branding=branding, pages=pages, content_hash=content_hash)
