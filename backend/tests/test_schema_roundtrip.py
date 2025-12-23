from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    CapabilityCategory,
    FieldMeta,
    FieldStatus,
    Provenance,
    ProvenanceType,
    RigMetricsPacket,
)


def test_rig_metrics_packet_roundtrip_byte_identical() -> None:
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
                evidence_ref="test:seed:rigmetrics",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )

    pkt = RigMetricsPacket(
        rig_id="rig.vl2.test.v1",
        module_count=1,
        category_counts={CapabilityCategory.sources: 1},
        modulation_budget=3.0,
        routing_flex_score=2.0,
        clock_coherence_score=1.0,
        chaos_headroom=0.5,
        learning_gradient_index=0.8,
        performance_density_index=0.2,
        meta=meta,
    )

    j1 = pkt.to_canonical_json()

    # round-trip
    pkt2 = RigMetricsPacket.model_validate_json(j1)
    j2 = pkt2.to_canonical_json()

    assert j1 == j2
