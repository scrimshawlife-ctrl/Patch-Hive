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


def test_attenuation_flag_clears_voltage_overage() -> None:
    nodes = list(_nodes())
    oscillator = nodes[1]
    nodes[1] = oscillator.model_copy(
        update={"ports": (oscillator.ports[0].model_copy(update={"voltage_max": 10}),)}
    )
    edge = _edge().model_copy(update={"attenuate": True})
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=7,
        intent="Attenuated high-level feed",
        nodes=nodes,
        edges=(edge,),
        created_at=NOW,
    )
    codes = {issue.code for issue in result.validation_report.issues}
    assert "ATTENUATION_REQUIRED" not in codes
    assert result.validation_report.valid is True


def test_signal_type_mismatch_is_blocking() -> None:
    nodes = list(_nodes())
    filter_node = nodes[0]
    nodes[0] = filter_node.model_copy(
        update={"ports": (filter_node.ports[0].model_copy(update={"signal_type": "cv"}),)}
    )
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=3,
        intent="Mismatched signal classes",
        nodes=nodes,
        edges=(_edge(),),
        created_at=NOW,
    )
    assert result.validation_report.valid is False
    assert "SIGNAL_TYPE_MISMATCH" in {issue.code for issue in result.validation_report.issues}


def test_unknown_signal_emits_warning_not_blocking() -> None:
    nodes = list(_nodes())
    filter_node = nodes[0]
    nodes[0] = filter_node.model_copy(
        update={"ports": (filter_node.ports[0].model_copy(update={"signal_type": "unknown"}),)}
    )
    edge = _edge().model_copy(update={"signal_type": "unknown"})
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=3,
        intent="Unknown capability path",
        nodes=nodes,
        edges=(edge,),
        created_at=NOW,
    )
    codes = {issue.code for issue in result.validation_report.issues}
    assert "UNSUPPORTED_CAPABILITY_CLAIM" in codes
    assert result.validation_report.valid is True


def test_reversed_direction_is_blocking() -> None:
    """Cable from input-only to output-only fails closed on directions."""
    nodes = (
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
                ),
            ),
        ),
    )
    edge = PatchEdge(
        edge_id="cable-reversed",
        source_port_id="filter.in",
        target_port_id="oscillator.out",
        signal_type="audio",
    )
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=1,
        intent="Reversed cable",
        nodes=nodes,
        edges=(edge,),
        created_at=NOW,
    )
    codes = {issue.code for issue in result.validation_report.issues}
    assert result.validation_report.valid is False
    assert "SOURCE_DIRECTION_INVALID" in codes
    assert "TARGET_DIRECTION_INVALID" in codes


def test_undeclared_feedback_cycle_is_blocking() -> None:
    nodes = (
        PatchNode(
            node_id="a",
            module_instance_id="a",
            label="A",
            ports=(
                PatchPort(
                    port_id="a.out",
                    module_instance_id="a",
                    module_port_id="out",
                    label="OUT",
                    direction="output",
                    signal_type="audio",
                ),
                PatchPort(
                    port_id="a.in",
                    module_instance_id="a",
                    module_port_id="in",
                    label="IN",
                    direction="input",
                    signal_type="audio",
                ),
            ),
        ),
        PatchNode(
            node_id="b",
            module_instance_id="b",
            label="B",
            ports=(
                PatchPort(
                    port_id="b.out",
                    module_instance_id="b",
                    module_port_id="out",
                    label="OUT",
                    direction="output",
                    signal_type="audio",
                ),
                PatchPort(
                    port_id="b.in",
                    module_instance_id="b",
                    module_port_id="in",
                    label="IN",
                    direction="input",
                    signal_type="audio",
                ),
            ),
        ),
    )
    edges = (
        PatchEdge(
            edge_id="ab",
            source_port_id="a.out",
            target_port_id="b.in",
            signal_type="audio",
        ),
        PatchEdge(
            edge_id="ba",
            source_port_id="b.out",
            target_port_id="a.in",
            signal_type="audio",
        ),
    )
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=9,
        intent="Undeclared feedback",
        nodes=nodes,
        edges=edges,
        created_at=NOW,
    )
    assert result.validation_report.valid is False
    assert "UNDECLARED_FEEDBACK_CYCLE" in {issue.code for issue in result.validation_report.issues}


def test_declared_feedback_cycle_is_allowed() -> None:
    nodes = (
        PatchNode(
            node_id="a",
            module_instance_id="a",
            label="A",
            ports=(
                PatchPort(
                    port_id="a.out",
                    module_instance_id="a",
                    module_port_id="out",
                    label="OUT",
                    direction="output",
                    signal_type="audio",
                ),
                PatchPort(
                    port_id="a.in",
                    module_instance_id="a",
                    module_port_id="in",
                    label="IN",
                    direction="input",
                    signal_type="audio",
                ),
            ),
        ),
        PatchNode(
            node_id="b",
            module_instance_id="b",
            label="B",
            ports=(
                PatchPort(
                    port_id="b.out",
                    module_instance_id="b",
                    module_port_id="out",
                    label="OUT",
                    direction="output",
                    signal_type="audio",
                ),
                PatchPort(
                    port_id="b.in",
                    module_instance_id="b",
                    module_port_id="in",
                    label="IN",
                    direction="input",
                    signal_type="audio",
                ),
            ),
        ),
    )
    edges = (
        PatchEdge(
            edge_id="ab",
            source_port_id="a.out",
            target_port_id="b.in",
            signal_type="audio",
            feedback_cycle_id="fb-1",
        ),
        PatchEdge(
            edge_id="ba",
            source_port_id="b.out",
            target_port_id="a.in",
            signal_type="audio",
            feedback_cycle_id="fb-1",
        ),
    )
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=9,
        intent="Declared feedback",
        nodes=nodes,
        edges=edges,
        created_at=NOW,
    )
    codes = {issue.code for issue in result.validation_report.issues}
    assert "UNDECLARED_FEEDBACK_CYCLE" not in codes
    assert result.validation_report.valid is True


def test_normalled_break_is_informational() -> None:
    edge = _edge().model_copy(update={"breaks_normal": True})
    result = compile_patch(
        run_id="run-1",
        rig_revision_id="rig-rev-1",
        seed=2,
        intent="Break a normal",
        nodes=_nodes(),
        edges=(edge,),
        created_at=NOW,
    )
    assert result.validation_report.valid is True
    assert "NORMALLED_CONNECTION_BREAK" in {issue.code for issue in result.validation_report.issues}


def test_empty_graph_compiles_with_startup_warning_only() -> None:
    result = compile_patch(
        run_id="run-empty",
        rig_revision_id="rig-rev-empty",
        seed=0,
        intent="Empty scaffold",
        nodes=(),
        edges=(),
        created_at=NOW,
    )
    # Prep steps from compiler include startup warning; empty graph has no blocking edges.
    assert result.validation_report.valid is True
    assert result.patch_graph.nodes == ()
    assert result.patch_graph.edges == ()
    assert len(result.patch_plan.steps) == 5
