from __future__ import annotations

import copy
import json
from typing import Any, Dict, List


def _sorted_wiring(wiring: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        wiring,
        key=lambda item: (
            item.get("from_module", ""),
            item.get("from_port", ""),
            item.get("to_module", ""),
            item.get("to_port", ""),
            item.get("cable_type", ""),
        ),
    )


def _sorted_parameters(params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        params,
        key=lambda item: (
            item.get("module_id", 0),
            item.get("parameter", ""),
            item.get("value", ""),
        ),
    )


def _sorted_variants(variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for variant in variants:
        wiring = variant.get("wiring_diff") or []
        variant["wiring_diff"] = sorted(
            wiring,
            key=lambda item: (
                item.get("action", ""),
                item.get("from_module", ""),
                item.get("from_port", ""),
                item.get("to_module", ""),
                item.get("to_port", ""),
            ),
        )
        params = variant.get("parameter_deltas") or []
        variant["parameter_deltas"] = sorted(
            params,
            key=lambda item: (item.get("module_id", 0), item.get("parameter", ""), item.get("to_value", "")),
        )

    def variant_key(item: Dict[str, Any]) -> tuple:
        return (
            item.get("variant_type", ""),
            json.dumps(item.get("wiring_diff", []), sort_keys=True),
            json.dumps(item.get("parameter_deltas", []), sort_keys=True),
        )

    return sorted(variants, key=variant_key)


def _sorted_macros(macros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(macros, key=lambda item: item.get("macro_id", ""))


def canonicalize_patchbook_payload(payload_dict: Dict[str, Any]) -> str:
    """
    Canonicalize PatchBook payload for deterministic hashing.
    """
    normalized = copy.deepcopy(payload_dict)
    normalized.pop("content_hash", None)

    pages = normalized.get("pages", [])
    for page in pages:
        inventory = page.get("module_inventory") or []
        page["module_inventory"] = sorted(
            inventory,
            key=lambda item: (
                item.get("module_id", 0),
                item.get("row_index", 0),
                item.get("start_hp", 0),
                item.get("name", ""),
            ),
        )

        io_inventory = page.get("io_inventory") or []
        page["io_inventory"] = sorted(
            io_inventory,
            key=lambda item: (
                item.get("module_id", 0),
                item.get("port_name", ""),
                item.get("direction", ""),
            ),
        )

        page["parameter_snapshot"] = _sorted_parameters(page.get("parameter_snapshot") or [])

        schematic = page.get("schematic") or {}
        wiring_list = schematic.get("wiring_list") or []
        schematic["wiring_list"] = _sorted_wiring(wiring_list)
        page["schematic"] = schematic

        patching_order = page.get("patching_order") or {}
        steps = patching_order.get("steps") or []
        patching_order["steps"] = sorted(steps, key=lambda item: item.get("step", 0))
        page["patching_order"] = patching_order

        macros = page.get("performance_macros")
        if macros:
            page["performance_macros"] = _sorted_macros(macros)

        variants = page.get("variants")
        if variants:
            page["variants"] = _sorted_variants(variants)

    normalized["pages"] = sorted(
        pages,
        key=lambda item: item.get("header", {}).get("patch_id", 0),
    )

    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))
