"""Patch validation rules."""
from __future__ import annotations

from typing import Dict, List, Tuple

from core.discovery import register_function
from patchhive.schemas import CanonicalRig, PatchGraph, ValidationReport


def _parse_contracts(contracts: List[str]) -> Dict[Tuple[str, str], Tuple[str, str]]:
    parsed: Dict[Tuple[str, str], Tuple[str, str]] = {}
    for contract in contracts:
        module_id, jack_name, direction, signal = contract.split(":")
        parsed[(module_id, jack_name)] = (direction, signal)
    return parsed


def validate_patch(patch_graph: PatchGraph, canonical_rig: CanonicalRig) -> ValidationReport:
    contracts = _parse_contracts(canonical_rig.explicit_signal_contracts)
    illegal_connections: List[str] = []
    for cable in patch_graph.cables:
        from_key = (cable.from_module_id, cable.from_port)
        to_key = (cable.to_module_id, cable.to_port)
        from_contract = contracts.get(from_key)
        to_contract = contracts.get(to_key)
        if from_contract is None or to_contract is None:
            illegal_connections.append(
                f"Unknown port {cable.from_module_id}:{cable.from_port} -> "
                f"{cable.to_module_id}:{cable.to_port}"
            )
            continue
        from_dir, from_signal = from_contract
        to_dir, to_signal = to_contract
        if from_dir == "input":
            illegal_connections.append("Cable starts from input-only jack.")
        if to_dir == "output":
            illegal_connections.append("Cable ends at output-only jack.")
        if from_signal != "unknown" and to_signal != "unknown" and from_signal != to_signal:
            illegal_connections.append("Signal type mismatch.")

    audio_present = any(cable.cable_type == "audio" for cable in patch_graph.cables)
    silence_risk = not audio_present
    runaway_risk = any(
        cable.from_module_id == cable.to_module_id for cable in patch_graph.cables
    )
    stability_score = max(0.0, 1.0 - (0.1 * len(illegal_connections)))
    if "seal" not in patch_graph.timeline:
        stability_score = min(stability_score, 0.4)
    return ValidationReport(
        illegal_connections=illegal_connections,
        silence_risk=silence_risk,
        runaway_risk=runaway_risk,
        stability_score=round(stability_score, 4),
    )


register_function(
    name="validate_patch",
    function=validate_patch,
    description="Validate patch legality and stability.",
    input_model="PatchGraph, CanonicalRig",
    output_model="ValidationReport",
)
