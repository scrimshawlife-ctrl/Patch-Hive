"""Graph-derived patch variant computation."""

from __future__ import annotations

from typing import Any

from modules.models import Module

from .models import PatchVariantComputed, WiringDiff, ParameterDelta
from .patching_order import MOD_TYPES, VOICE_TYPES


def _generate_stabilize_variant(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    has_feedback: bool,
) -> PatchVariantComputed | None:
    """Generate a stabilized version of the patch."""
    if not has_feedback and len(connections) < 5:
        return None  # Already stable

    wiring_diffs = []
    param_deltas = []

    # Remove feedback cables if present
    if has_feedback:
        # Simplified: remove last CV connection as proxy for feedback
        cv_conns = [
            conn for conn in connections if (conn.get("cable_type") or "").lower() == "cv"
        ]
        if cv_conns:
            last_cv = cv_conns[-1]
            from_module = modules.get(last_cv.get("from_module_id"))
            to_module = modules.get(last_cv.get("to_module_id"))
            if from_module and to_module:
                wiring_diffs.append(
                    WiringDiff(
                        action="remove",
                        from_module=from_module.name,
                        from_port=last_cv.get("from_port", ""),
                        to_module=to_module.name,
                        to_port=last_cv.get("to_port", ""),
                        cable_type=last_cv.get("cable_type", "cv"),
                    )
                )

    # Suggest reducing modulation depth
    mod_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in MOD_TYPES
    ]
    for mod in mod_modules[:2]:
        param_deltas.append(
            ParameterDelta(
                module_name=mod.name,
                parameter="Depth/Amount",
                from_value="70%",
                to_value="30%",
            )
        )

    if not wiring_diffs and not param_deltas:
        return None

    return PatchVariantComputed(
        variant_type="stabilize",
        wiring_diff=wiring_diffs,
        parameter_deltas=param_deltas,
        behavioral_delta_summary="Reduced feedback and modulation for stable, predictable output",
    )


def _generate_wild_variant(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PatchVariantComputed | None:
    """Generate a wild/experimental version of the patch."""
    wiring_diffs = []
    param_deltas = []

    # Add feedback if not present
    voice_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in VOICE_TYPES
    ]
    mod_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in MOD_TYPES
    ]

    if voice_modules and mod_modules:
        voice = voice_modules[0]
        mod = mod_modules[0]
        wiring_diffs.append(
            WiringDiff(
                action="add",
                from_module=voice.name,
                from_port="Output",
                to_module=mod.name,
                to_port="CV In",
                cable_type="cv",
            )
        )

    # Increase modulation depth
    for mod in mod_modules[:2]:
        param_deltas.append(
            ParameterDelta(
                module_name=mod.name,
                parameter="Depth/Rate",
                from_value="30%",
                to_value="80%",
            )
        )

    if not wiring_diffs and not param_deltas:
        return None

    return PatchVariantComputed(
        variant_type="wild",
        wiring_diff=wiring_diffs,
        parameter_deltas=param_deltas,
        behavioral_delta_summary="Increased feedback and modulation for chaotic, evolving textures",
    )


def _generate_performance_variant(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PatchVariantComputed | None:
    """Generate a performance-optimized version."""
    param_deltas = []

    # Optimize VCA levels for live control
    vca_modules = [
        m for m in modules.values() if "VCA" in (m.module_type or "").upper()
    ]
    for vca in vca_modules[:2]:
        param_deltas.append(
            ParameterDelta(
                module_name=vca.name,
                parameter="Level",
                from_value="Current",
                to_value="50% (balanced for mixing)",
            )
        )

    # Set LFO rates for live tweaking
    lfo_modules = [
        m for m in modules.values() if "LFO" in (m.module_type or "").upper()
    ]
    for lfo in lfo_modules[:1]:
        param_deltas.append(
            ParameterDelta(
                module_name=lfo.name,
                parameter="Rate",
                from_value="Current",
                to_value="2-5Hz (visible modulation)",
            )
        )

    if not param_deltas:
        return None

    return PatchVariantComputed(
        variant_type="performance",
        wiring_diff=[],
        parameter_deltas=param_deltas,
        behavioral_delta_summary="Optimized levels and rates for live performance control",
    )


def compute_patch_variants(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    has_feedback: bool = False,
) -> list[PatchVariantComputed]:
    """Compute graph-derived patch variants."""
    variants = []

    stabilize = _generate_stabilize_variant(connections, modules, has_feedback)
    if stabilize:
        variants.append(stabilize)

    wild = _generate_wild_variant(connections, modules)
    if wild:
        variants.append(wild)

    performance = _generate_performance_variant(connections, modules)
    if performance:
        variants.append(performance)

    return variants
