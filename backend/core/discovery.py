"""Dynamic Function Discovery registry for AAL-core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass(frozen=True)
class FunctionDescriptor:
    name: str
    function: Callable[..., Any]
    description: str
    input_model: Optional[str] = None
    output_model: Optional[str] = None


_registry: Dict[str, FunctionDescriptor] = {}


def register_function(
    name: str,
    function: Callable[..., Any],
    description: str,
    input_model: Optional[str] = None,
    output_model: Optional[str] = None,
) -> FunctionDescriptor:
    descriptor = FunctionDescriptor(
        name=name,
        function=function,
        description=description,
        input_model=input_model,
        output_model=output_model,
    )
    _registry[name] = descriptor
    return descriptor


def get_registered_functions() -> Dict[str, FunctionDescriptor]:
    return dict(_registry)


def clear_registry() -> None:
    _registry.clear()
