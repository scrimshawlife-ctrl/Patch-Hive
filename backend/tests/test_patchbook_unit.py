"""Unit tests for PatchBook export pipeline."""

from __future__ import annotations

from sqlalchemy.orm import Session

from patches.models import Patch
from racks.models import Rack

from export.patchbook.build import build_patchbook_pdf_bytes_from_payload
from export.patchbook.builder import build_patchbook_document
from export.patchbook.models import (
    PatchBookExportRequest,
    PatchBookTier,
    PATCHBOOK_TEMPLATE_VERSION,
)
from export.patchbook import pdf_meta


def _create_patch(db_session: Session, rack: Rack) -> Patch:
    patch = Patch(
        rack_id=rack.id,
        run_id=None,
        name="Test Patch",
        category="Voice",
        description="Test patch description",
        connections=[
            {
                "from_module_id": rack.modules[0].module_id,
                "from_port": "Audio Out",
                "to_module_id": rack.modules[1].module_id,
                "to_port": "Audio In",
                "cable_type": "audio",
            }
        ],
        generation_seed=42,
        generation_version="1.0.0",
        engine_config={"parameters": {str(rack.modules[0].module_id): {"Tune": "12 o'clock"}}},
    )
    db_session.add(patch)
    db_session.commit()
    db_session.refresh(patch)
    return patch


def test_build_patchbook_pdf_bytes_deterministic(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    patch = _create_patch(db_session, sample_rack_basic)

    payload = PatchBookExportRequest(rack_id=sample_rack_basic.id, patch_ids=[patch.id])
    pdf_bytes, content_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)
    pdf_bytes_repeat, repeat_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 10_000
    assert content_hash == repeat_hash
    assert PATCHBOOK_TEMPLATE_VERSION.encode("utf-8") in pdf_bytes
    assert content_hash.encode("utf-8") in pdf_bytes
    assert b"CreationDate" not in pdf_bytes


def test_patchbook_hash_stable_with_metadata_variation(
    db_session: Session,
    sample_rack_basic: Rack,
    monkeypatch,
) -> None:
    patch = _create_patch(db_session, sample_rack_basic)
    payload = PatchBookExportRequest(rack_id=sample_rack_basic.id, patch_ids=[patch.id])

    _, first_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)
    monkeypatch.setattr(pdf_meta, "apply_deterministic_pdf_metadata", lambda *args, **kwargs: None)
    _, second_hash = build_patchbook_pdf_bytes_from_payload(db_session, payload)

    assert first_hash == second_hash


def test_tier_gating_free_has_no_computed_panels(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    """Free tier should not include any computed panels."""
    patch = _create_patch(db_session, sample_rack_basic)
    patches = [patch]

    document = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.FREE
    )

    assert document.tier == PatchBookTier.FREE
    assert len(document.pages) == 1

    page = document.pages[0]
    assert page.fingerprint is None
    assert page.stability is None
    assert page.troubleshooting is None
    assert page.performance_macros is None
    assert page.computed_variants is None

    assert document.golden_rack is None
    assert document.compatibility is None
    assert document.learning_path is None


def test_tier_gating_core_has_basic_panels(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    """Core tier should include fingerprint, stability, troubleshooting, and macros."""
    patch = _create_patch(db_session, sample_rack_basic)
    patches = [patch]

    document = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.CORE
    )

    assert document.tier == PatchBookTier.CORE
    assert len(document.pages) == 1

    page = document.pages[0]
    assert page.fingerprint is not None
    assert page.fingerprint.topology_hash
    assert page.fingerprint.complexity_vector.cable_count > 0

    assert page.stability is not None
    assert page.stability.stability_class in {"Stable", "Sensitive", "Wild"}

    assert page.troubleshooting is not None
    assert len(page.troubleshooting.no_sound_checks) > 0

    # Macros might be None if no performance modules
    # Computed variants should be None in Core tier
    assert page.computed_variants is None

    # Book-level analytics should be None in Core tier
    assert document.golden_rack is None
    assert document.compatibility is None
    assert document.learning_path is None


def test_tier_gating_pro_has_all_panels(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    """Pro tier should include all computed panels and book analytics."""
    patch = _create_patch(db_session, sample_rack_basic)
    patches = [patch]

    document = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.PRO
    )

    assert document.tier == PatchBookTier.PRO
    assert len(document.pages) == 1

    page = document.pages[0]
    assert page.fingerprint is not None
    assert page.stability is not None
    assert page.troubleshooting is not None

    # Computed variants should be present in Pro tier
    assert page.computed_variants is not None or page.computed_variants == []

    # Book-level analytics should be present in Pro tier
    assert document.golden_rack is not None
    assert document.compatibility is not None
    assert document.learning_path is not None


def test_tier_content_hash_deterministic_per_tier(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    """Same payload + tier should produce same content hash."""
    patch = _create_patch(db_session, sample_rack_basic)

    payload_core = PatchBookExportRequest(
        rack_id=sample_rack_basic.id, patch_ids=[patch.id], tier=PatchBookTier.CORE
    )
    payload_pro = PatchBookExportRequest(
        rack_id=sample_rack_basic.id, patch_ids=[patch.id], tier=PatchBookTier.PRO
    )

    _, hash_core_1 = build_patchbook_pdf_bytes_from_payload(db_session, payload_core)
    _, hash_core_2 = build_patchbook_pdf_bytes_from_payload(db_session, payload_core)

    _, hash_pro_1 = build_patchbook_pdf_bytes_from_payload(db_session, payload_pro)
    _, hash_pro_2 = build_patchbook_pdf_bytes_from_payload(db_session, payload_pro)

    # Same tier should produce same hash
    assert hash_core_1 == hash_core_2
    assert hash_pro_1 == hash_pro_2

    # Different tiers should produce different hashes (due to different content)
    assert hash_core_1 != hash_pro_1


def test_higher_tier_is_superset(
    db_session: Session,
    sample_rack_basic: Rack,
) -> None:
    """Higher tiers should contain strictly more data than lower tiers."""
    patch = _create_patch(db_session, sample_rack_basic)
    patches = [patch]

    doc_free = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.FREE
    )
    doc_core = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.CORE
    )
    doc_pro = build_patchbook_document(
        db_session, sample_rack_basic, patches, tier=PatchBookTier.PRO
    )

    # Free has no computed panels
    free_has_computed = any(
        page.fingerprint or page.stability or page.troubleshooting
        for page in doc_free.pages
    )
    assert not free_has_computed

    # Core has basic computed panels
    core_has_computed = any(
        page.fingerprint and page.stability and page.troubleshooting
        for page in doc_core.pages
    )
    assert core_has_computed

    # Pro has all of Core plus variants and book analytics
    pro_has_all = any(
        page.fingerprint and page.stability and page.troubleshooting
        for page in doc_pro.pages
    )
    assert pro_has_all
    assert doc_pro.golden_rack is not None
    assert doc_pro.compatibility is not None
    assert doc_pro.learning_path is not None
