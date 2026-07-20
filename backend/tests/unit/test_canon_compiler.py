"""Deterministic compiler and safety validation tests."""

from datetime import datetime, timezone

from hypothesis import given, strategies as st

from canon.compiler import compile_patch
from canon.contracts import PatchEdge, PatchNode, PatchPort

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _nodes() -> tuple[PatchNode, ...]:
    return (
        PatchNode(
            node_id="filter",
            module_instance_id="filter",
            label="Filter",
            ports=(
                PatchPort(
                    port_id="filter.in",
                    module_instance_id="filter",
                    module_port_id="in",
                    label="IN",
                    direction="input",
                    signal_type="audio",
                    voltage_min=-5,
                    voltage_max=5,
                ),
            ),
        ),
        PatchNode(
            node_id="oscillator",
            module_instance_id="oscillator",
            label="Oscillator",
            ports=(
                PatchPort(
                    port_id="oscillator.out",
                    module_instance_id="oscillator",
                    module_port_id="out",
                    label="OUT",
                    direction="output",
                    signal_type="audio",
                    voltage_min=-5,
                    voltage_max=5,
                ),
            ),
        ),
    )


def _edge() -> PatchEdge:
    return PatchEdge(
        edge_id="cable-1",
        source_port_id="oscillator.out",
        target_port_id="filter.in",
        signal_type="audio",
    )


@given(st.integers(min_value=0, max_value=2**31 - 1), st.booleans())
def test_compilation_is_byte_stable_for_equivalent_input(seed: int, reverse: bool) -> None:
    nodes = tuple(reversed(_nodes())) if reverse else _nodes()
    first = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=seed,
        intent="A stable subtractive voice",
        nodes=nodes,
        edges=(_edge(),),
        created_at=NOW,
    )
    second = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=seed,
        intent="A stable subtractive voice",
        nodes=_nodes(),
        edges=(_edge(),),
        created_at=NOW,
    )
    assert first.canonical_json() == second.canonical_json()
    assert first.patch_graph.canonical_hash == second.patch_graph.canonical_hash
    assert first.artifact_manifest.canonical_hash == second.artifact_manifest.canonical_hash


def test_compiler_emits_complete_plan_receipts_manifest_and_variation() -> None:
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=7,
        intent="A stable subtractive voice",
        nodes=_nodes(),
        edges=(_edge(),),
        created_at=NOW,
    )
    assert [step.phase for step in result.patch_plan.steps] == [
        "prep",
        "threshold",
        "peak",
        "release",
        "seal",
    ]
    assert result.validation_report.valid is True
    assert len(result.variations) == 1
    assert len(result.stage_receipts) == 3
    assert {item.path for item in result.artifact_manifest.artifacts} == {
        "patch_graph.json",
        "patch_plan.json",
        "validation_report.json",
    }


def test_compiler_matches_golden_replay_receipt() -> None:
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=7,
        intent="A stable subtractive voice",
        nodes=_nodes(),
        edges=(_edge(),),
        created_at=NOW,
    )
    assert result.canonical_hash_value() == (
        "c2356d416b9784d4487ffadf1fc6aafb974644f0767a5a36cba44d7f397934ee"
    )
    assert result.patch_graph.canonical_hash == (
        "21813066fa6fa1a3ae4df83646bae3aef40d78df1255b6b7fb27a8729c26f509"
    )
    assert result.artifact_manifest.canonical_hash == (
        "7c40f8e023ebbc877cd7fd8492ce35bd12a411d5aae3408ffe76abbd70c53f0c"
    )


def test_voltage_overage_requires_attenuation() -> None:
    nodes = list(_nodes())
    oscillator = nodes[1]
    nodes[1] = oscillator.model_copy(
        update={"ports": (oscillator.ports[0].model_copy(update={"voltage_max": 10}),)}
    )
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=7,
        intent="Unsafe voltage fixture",
        nodes=nodes,
        edges=(_edge(),),
        created_at=NOW,
    )
    assert result.validation_report.valid is False
    assert "ATTENUATION_REQUIRED" in {issue.code for issue in result.validation_report.issues}
