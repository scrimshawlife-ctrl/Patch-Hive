from __future__ import annotations

from patchhive.schemas import CanonicalRig, RigMetricsPacket


def map_metrics(rig: CanonicalRig) -> RigMetricsPacket:
    """
    Deterministic metrics mapping placeholder.
    """
    return RigMetricsPacket(routing_flex_score=0.75)
