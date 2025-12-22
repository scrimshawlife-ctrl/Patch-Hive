from __future__ import annotations

from typing import Optional

from patchhive.gallery.function_store import FunctionRegistryStore


def function_matches(
    fn_store: FunctionRegistryStore,
    jack_label: str,
    required_any_of: tuple[str, ...],
) -> bool:
    """
    Deterministic match:
      - check alias index for jack_label -> function_id
      - accept if in required_any_of
    """
    fid = fn_store.lookup_alias(jack_label)
    if not fid:
        return False
    return fid in set(required_any_of)
