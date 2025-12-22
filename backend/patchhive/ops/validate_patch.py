"""Validate generated patch graphs."""

from __future__ import annotations

from patchhive.schemas import JackSignalType, PatchGraph, ValidationIssue, ValidationReport


def validate_patch_v1(graph: PatchGraph) -> ValidationReport:
    issues: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    for edge in graph.edges:
        if ":out" not in edge.from_jack or ":in" not in edge.to_jack:
            issues.append(
                ValidationIssue(
                    code="illegal_jack_contract",
                    message=f"Invalid jack direction on edge {edge.edge_id}",
                    severity="error",
                )
            )
    if not graph.edges:
        warnings.append(
            ValidationIssue(
                code="silence_risk",
                message="No patch edges found; silence risk.",
                severity="warning",
            )
        )
    if any(edge.signal_type == JackSignalType.CV for edge in graph.edges) and any(
        edge.signal_type == JackSignalType.AUDIO for edge in graph.edges
    ):
        warnings.append(
            ValidationIssue(
                code="runaway_risk",
                message="Mixed CV and audio routing detected; monitor gain staging.",
                severity="warning",
            )
        )
    stability_score = max(0.0, 1.0 - (0.2 * len(issues)) - (0.1 * len(warnings)))
    return ValidationReport(
        rig_id=graph.rig_id,
        issues=issues,
        warnings=warnings,
        stability_score=stability_score,
    )
