from pathlib import Path

from canon import contracts

REQUIRED_CONTRACTS = {
    "DetectedModule",
    "ResolvedModuleRef",
    "EvidenceRecord",
    "ModuleGalleryEntry",
    "ModuleRevision",
    "RigSpec",
    "CanonicalRig",
    "RigRevision",
    "RigMetricsPacket",
    "SuggestedLayout",
    "PatchGraph",
    "PatchNode",
    "PatchPort",
    "PatchEdge",
    "PatchPlan",
    "PatchStep",
    "PatchVariation",
    "ValidationIssue",
    "ValidationReport",
    "SymbolicPatchEnvelope",
    "ArtifactManifest",
    "StageReceipt",
    "GenerationRequest",
    "GenerationJob",
    "ExportRequest",
    "ExportRecord",
    "CreditLedgerEntry",
    "StripeEventRecord",
    "AdminAuditEvent",
    "UserPatchAnnotation",
}


def test_typescript_bindings_cover_versioned_backend_contracts() -> None:
    binding_path = Path(__file__).resolve().parents[3] / "frontend" / "src" / "types" / "canon.ts"
    binding = binding_path.read_text(encoding="utf-8")
    assert contracts.SCHEMA_VERSION in binding
    for name in REQUIRED_CONTRACTS:
        assert hasattr(contracts, name), f"missing backend contract: {name}"
        assert f"interface {name}" in binding, f"missing TypeScript binding: {name}"
