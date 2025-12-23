"""Build PatchBook document from database models."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule

from .branding import get_patchbook_branding
from .compute_book_analytics import (
    compute_compatibility_report,
    compute_golden_rack_analysis,
    compute_learning_path,
)
from .compute_fingerprint import compute_patch_fingerprint
from .compute_macros import compute_performance_macros
from .compute_stability import compute_stability_envelope
from .compute_troubleshooting import compute_troubleshooting_tree
from .compute_variants import compute_patch_variants
from .models import (
    IOEndpoint,
    ParameterSnapshot,
    PatchBookDocument,
    PatchBookHeader,
    PatchBookPage,
    PatchBookTier,
    PatchModulePosition,
)
from .patching_order import generate_patching_order
from .render_schematic import render_patch_schematic
from .tier_gating import TierFeatures


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

    features = TierFeatures(tier)

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

        # Compute tier-gated panels
        fingerprint = None
        stability = None
        troubleshooting = None
        performance_macros = None
        computed_variants = None

        if features.patch_fingerprint:
            fingerprint = compute_patch_fingerprint(patch.connections, modules)

        if features.stability_envelope:
            parameters = patch.engine_config.get("parameters", {}) if patch.engine_config else {}
            has_feedback = (
                fingerprint.complexity_vector.feedback_present if fingerprint else False
            )
            stability = compute_stability_envelope(
                patch.connections, modules, parameters, has_feedback
            )

        if features.troubleshooting_tree:
            troubleshooting = compute_troubleshooting_tree(patch.connections, modules)

        if features.performance_macros:
            performance_macros = compute_performance_macros(patch.connections, modules)
            if not performance_macros:
                performance_macros = None

        if features.computed_variants:
            has_feedback = (
                fingerprint.complexity_vector.feedback_present if fingerprint else False
            )
            computed_variants = compute_patch_variants(
                patch.connections, modules, has_feedback
            )
            if not computed_variants:
                computed_variants = None

        pages.append(
            PatchBookPage(
                header=header,
                module_inventory=module_inventory,
                io_inventory=io_inventory,
                parameter_snapshot=parameter_snapshot,
                schematic=schematic,
                patching_order=patching_order,
                variants=None,
                fingerprint=fingerprint,
                stability=stability,
                troubleshooting=troubleshooting,
                performance_macros=performance_macros,
                computed_variants=computed_variants,
            )
        )

    # Compute book-level analytics
    golden_rack = None
    compatibility = None
    learning_path = None

    if features.golden_rack_analysis:
        golden_rack = compute_golden_rack_analysis(rack_modules, modules, patches)

    if features.compatibility_report:
        compatibility = compute_compatibility_report(rack_modules, modules, patches)

    if features.learning_path:
        learning_path = compute_learning_path(patches, modules)

    branding = get_patchbook_branding()
    return PatchBookDocument(
        branding=branding,
        pages=pages,
        content_hash=content_hash,
        tier=tier,
        golden_rack=golden_rack,
        compatibility=compatibility,
        learning_path=learning_path,
    )
