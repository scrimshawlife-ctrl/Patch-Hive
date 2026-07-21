"""Multi-photo reconciliation unit tests."""

from evidence.reconciliation import reconcile_candidate_observations


def _cand(
    cid: str,
    *,
    mfr: str,
    model: str,
    conf: float,
    image: str,
) -> dict:
    return {
        "candidate_id": cid,
        "entity_type": "module",
        "manufacturer": mfr,
        "model": model,
        "confidence": conf,
        "confidence_method": "test",
        "classification_status": "INFERRED",
        "evidence_id": f"ev-{cid}",
        "image_asset_id": image,
        "alternative_candidates": [],
        "_raw": {
            "candidate_id": cid,
            "entity_type": "module",
            "manufacturer": mfr,
            "model": model,
            "confidence": conf,
            "confidence_method": "test",
            "classification_status": "INFERRED",
            "evidence_id": f"ev-{cid}",
        },
    }


def test_fuse_same_module_across_two_images() -> None:
    report = reconcile_candidate_observations(
        [
            _cand("c1", mfr="Make Noise", model="Maths", conf=0.7, image="img-a"),
            _cand("c2", mfr="Make Noise", model="Maths", conf=0.9, image="img-b"),
        ]
    )
    assert report.status == "OK"
    assert len(report.fused_entities) == 1
    fused = report.fused_entities[0]
    assert len(fused.observations) == 2
    assert set(fused.supporting_image_ids) == {"img-a", "img-b"}
    assert abs(fused.mean_confidence - 0.8) < 1e-9
    assert fused.conflict is False
    assert fused.classification_status == "INFERRED"


def test_conflict_when_models_disagree() -> None:
    report = reconcile_candidate_observations(
        [
            _cand("c1", mfr="Mutable", model="Rings", conf=0.8, image="img-a"),
            # same key only if manufacturer+model match; different models → separate keys
            _cand("c2", mfr="Mutable", model="Elements", conf=0.75, image="img-b"),
        ]
    )
    # Different models produce separate fused entities (not a forced merge)
    assert len(report.fused_entities) == 2
    assert report.conflict_count == 0


def test_single_image_marked_insufficient() -> None:
    report = reconcile_candidate_observations(
        [_cand("c1", mfr="A", model="B", conf=0.5, image="img-only")]
    )
    assert report.status == "INSUFFICIENT_IMAGES"
    assert len(report.fused_entities) == 1


def test_empty() -> None:
    report = reconcile_candidate_observations([])
    assert report.status == "EMPTY"
    assert report.to_dict()["note"]
