"""Build PatchBook document from database models."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule

from .branding import get_patchbook_branding
from .book_analytics import (
    compute_compatibility_report,
    compute_golden_rack_arrangement,
    compute_learning_path,
)
from .computation import (
    PatchInsights,
    compute_patch_fingerprint,
    compute_patch_variants,
    compute_performance_macros,
    compute_stability_envelope,
    compute_troubleshooting_tree,
)
from .models import (
    IOEndpoint,
    ParameterSnapshot,
    PatchBookDocument,
    PatchBookHeader,
    PatchBookPage,
    PatchModulePosition,
    PatchBookTier,
)
from .patching_order import generate_patching_order
from .render_schematic import render_patch_schematic
from .tiers import get_tier_features


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
    tier: PatchBookTier = PatchBookTier.CORE,
    content_hash: str | None = None,
) -> PatchBookDocument:
    """Build PatchBook document from rack and patches."""
    tier_features = get_tier_features(tier)
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
    insights: list[PatchInsights] = []
    learning_payload: list[dict[str, str | int]] = []
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

        parameter_payload = [
            {
                "module_id": snapshot.module_id,
                "module_name": snapshot.module_name,
                "parameter": snapshot.parameter,
                "value": snapshot.value,
            }
            for snapshot in parameter_snapshot
        ]

        patch_fingerprint = None
        patch_insight = None
        if tier_features.patch_fingerprint:
            patch_fingerprint, patch_insight = compute_patch_fingerprint(
                patch.connections,
                parameter_payload,
                module_inventory,
                allow_rack_fit=tier_features.rack_fit_score,
            )
            insights.append(patch_insight)
            learning_payload.append({"patch_id": patch.id, "patch_name": patch.name})

        stability_envelope = (
            compute_stability_envelope(patch.connections, parameter_payload, module_inventory, patch_insight)
            if tier_features.stability_envelope and patch_insight
            else None
        )

        troubleshooting_tree = (
            compute_troubleshooting_tree(patch.connections, parameter_payload, module_inventory)
            if tier_features.troubleshooting_tree
            else None
        )

        performance_macros = (
            compute_performance_macros(parameter_payload) if tier_features.performance_macros else None
        )

        variants = (
            compute_patch_variants(patch.connections, parameter_payload, module_inventory, patch_insight)
            if tier_features.patch_variants and patch_insight
            else None
        )

        pages.append(
            PatchBookPage(
                header=header,
                module_inventory=module_inventory,
                io_inventory=io_inventory,
                parameter_snapshot=parameter_snapshot,
                schematic=schematic,
                patching_order=patching_order,
                variants=variants if variants else None,
                patch_fingerprint=patch_fingerprint,
                stability_envelope=stability_envelope,
                troubleshooting_tree=troubleshooting_tree,
                performance_macros=performance_macros if performance_macros else None,
            )
        )

    branding = get_patchbook_branding()
    golden_rack_arrangement = (
        compute_golden_rack_arrangement(pages[0].module_inventory, [conn for patch in patches for conn in patch.connections])
        if tier_features.golden_rack_arrangement and pages
        else None
    )
    compatibility_report = (
        compute_compatibility_report(pages[0].module_inventory, insights) if tier_features.compatibility_report else None
    )
    learning_path = (
        compute_learning_path(learning_payload, insights) if tier_features.learning_path and insights else None
    )

    return PatchBookDocument(
        branding=branding,
        pages=pages,
        content_hash=content_hash,
        tier_name=tier.value,
        golden_rack_arrangement=golden_rack_arrangement,
        compatibility_report=compatibility_report,
        learning_path=learning_path,
    )
