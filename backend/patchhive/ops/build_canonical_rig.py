"""Build a canonical rig representation from RigSpec and gallery references."""

from __future__ import annotations

from patchhive.schemas import (
    CanonicalModule,
    CanonicalRig,
    Provenance,
    ProvenanceStatus,
    ProvenanceType,
    ResolvedModuleRef,
    RigSpec,
)


def _canonical_id(module_name: str, index: int) -> str:
    slug = "".join(ch for ch in module_name.lower() if ch.isalnum())
    return f"{slug or 'module'}-{index:02d}"


def build_canonical_rig_v1(
    rig_spec: RigSpec,
    resolved_refs: list[ResolvedModuleRef],
) -> CanonicalRig:
    modules: list[CanonicalModule] = []
    normalled_edges = []
    for idx, module_input in enumerate(rig_spec.modules):
        ref = resolved_refs[idx] if idx < len(resolved_refs) else None
        module_spec = ref.module_spec if ref and ref.module_spec else None
        if module_spec is None:
            continue
        canonical_id = _canonical_id(module_spec.name, idx)
        status = ref.status if ref else ProvenanceStatus.MISSING
        modules.append(
            CanonicalModule(
                canonical_id=canonical_id,
                module_spec=module_spec,
                provenance=Provenance(type=ProvenanceType.GALLERY),
                confidence=ref.match_confidence if ref else 0.0,
                status=status,
                observed_position=module_input.position_hint.value if module_input.position_hint else None,
            )
        )
        normalled_edges.extend(module_spec.normalled_edges)
    return CanonicalRig(rig_id=rig_spec.rig_id, modules=modules, normalled_edges=normalled_edges)
