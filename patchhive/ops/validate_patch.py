from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

from patchhive.schemas import (
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    JackDir,
    PatchGraph,
    Provenance,
    ProvenanceType,
    SignalKind,
    ValidationReport,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(patch_id: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"patch:{patch_id}",
                method="validate_patch.v1",
            )
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )


def _jack_index(canon: CanonicalRig) -> Dict[str, Tuple[JackDir, SignalKind]]:
    """
    jack_id -> (dir, signal_kind)
    """
    idx: Dict[str, Tuple[JackDir, SignalKind]] = {}
    for m in canon.modules:
        for j in m.jacks:
            idx[j.jack_id] = (j.dir, j.signal.kind)
    return idx


def _is_compatible(src: SignalKind, dst: SignalKind) -> bool:
    """
    Conservative compatibility rules:
    - audio can go to audio or cv_or_audio
    - cv can go to cv or cv_or_audio
    - clock/gate/trigger can go to clock/gate/trigger/cv_or_audio (many inputs tolerate)
    - unknown is compatible with unknown/cv_or_audio only
    """
    if dst == SignalKind.cv_or_audio:
        return True

    if src == SignalKind.audio:
        return dst in {SignalKind.audio}
    if src in {SignalKind.cv, SignalKind.lfo, SignalKind.envelope, SignalKind.random, SignalKind.pitch_cv}:
        return dst in {SignalKind.cv, SignalKind.lfo, SignalKind.envelope, SignalKind.random, SignalKind.pitch_cv}
    if src in {SignalKind.clock, SignalKind.gate, SignalKind.trigger}:
        return dst in {SignalKind.clock, SignalKind.gate, SignalKind.trigger}
    if src == SignalKind.unknown:
        return dst in {SignalKind.unknown}
    # default safe-ish
    return src == dst


def _build_module_graph(cables: List[Tuple[str, str]]) -> Dict[str, Set[str]]:
    """
    Build module-level adjacency graph from jack_ids assumed to be 'module.jack' style.
    If not, we fall back to jack prefix before first '.'.
    """

    def mod_of(jack_id: str) -> str:
        # instance_id not embedded here in v1; assume jack_id prefix is module-ish.
        # This remains a *risk* but still useful for runaway/cycle heuristics.
        return jack_id.split(".", 1)[0] if "." in jack_id else jack_id

    g: Dict[str, Set[str]] = defaultdict(set)
    for a, b in cables:
        ma, mb = mod_of(a), mod_of(b)
        if ma != mb:
            g[ma].add(mb)
    return g


def _has_cycle(graph: Dict[str, Set[str]]) -> bool:
    """
    Detect directed cycle via Kahn-like approach.
    """
    indeg: Dict[str, int] = defaultdict(int)
    nodes: Set[str] = set(graph.keys())
    for u, vs in graph.items():
        nodes.add(u)
        for v in vs:
            nodes.add(v)
            indeg[v] += 1
    q = deque([n for n in nodes if indeg[n] == 0])
    seen = 0
    while q:
        n = q.popleft()
        seen += 1
        for v in graph.get(n, set()):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen != len(nodes)


def validate_patch(canon: CanonicalRig, patch: PatchGraph) -> ValidationReport:
    idx = _jack_index(canon)

    illegal: List[str] = []
    silence_risk: List[str] = []
    runaway_risk: List[str] = []

    # Direction & compatibility checks
    for c in patch.cables:
        if c.from_jack not in idx:
            illegal.append(f"Unknown from_jack: {c.from_jack}")
            continue
        if c.to_jack not in idx:
            illegal.append(f"Unknown to_jack: {c.to_jack}")
            continue

        from_dir, from_kind = idx[c.from_jack]
        to_dir, to_kind = idx[c.to_jack]

        if from_dir not in {JackDir.out, JackDir.bidir}:
            illegal.append(f"from_jack not output-capable: {c.from_jack} ({from_dir})")
        if to_dir not in {JackDir.in_, JackDir.bidir}:
            illegal.append(f"to_jack not input-capable: {c.to_jack} ({to_dir})")

        if not _is_compatible(from_kind, to_kind):
            illegal.append(f"Signal mismatch: {c.from_jack}({from_kind}) -> {c.to_jack}({to_kind})")

    # Silence risk heuristic: require at least one audio-ish cable reaching an IO/External-ish target.
    # Since categories aren't embedded here, we proxy: any cable whose src kind is audio and dest kind is audio/cv_or_audio.
    audio_paths = 0
    for c in patch.cables:
        if c.from_jack in idx and c.to_jack in idx:
            _, fk = idx[c.from_jack]
            _, tk = idx[c.to_jack]
            if fk == SignalKind.audio and tk in {SignalKind.audio, SignalKind.cv_or_audio}:
                audio_paths += 1
    if audio_paths == 0:
        silence_risk.append("No audio path detected (no audio -> audio/cv_or_audio connections).")

    # Runaway risk heuristic: detect cycles on module-level adjacency
    edges = [(c.from_jack, c.to_jack) for c in patch.cables]
    mg = _build_module_graph(edges)
    if _has_cycle(mg):
        runaway_risk.append("Directed cycle detected in module graph (potential feedback/runaway risk).")

    # Stability score: start from 1, subtract penalties
    score = 1.0
    score -= min(0.6, 0.15 * len(illegal))
    score -= min(0.3, 0.10 * len(silence_risk))
    score -= min(0.3, 0.10 * len(runaway_risk))
    score = 0.0 if score < 0.0 else (1.0 if score > 1.0 else score)

    return ValidationReport(
        patch_id=patch.patch_id,
        illegal_connections=illegal,
        silence_risk=silence_risk,
        runaway_risk=runaway_risk,
        stability_score=float(score),
        meta=_meta_derived(patch.patch_id),
    )
