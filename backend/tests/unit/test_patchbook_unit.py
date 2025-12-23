"""
Unit tests for Patch Book PDF export (PAID FEATURE).

Tests determinism, structure, and content integrity.
"""

from datetime import datetime
from hashlib import sha256

import pytest
from sqlalchemy.orm import Session

from export.pdf import (
    PATCHBOOK_TEMPLATE_VERSION,
    build_patchbook_pdf_bytes,
    compute_patchbook_content_hash,
)
from patches.models import Patch
from racks.models import Rack


def test_patchbook_pdf_returns_valid_pdf_bytes(
    db_session: Session, sample_rack_basic: Rack
):
    """Test that patchbook export returns valid PDF bytes."""
    pdf_bytes = build_patchbook_pdf_bytes(db_session, sample_rack_basic)

    # Assert PDF header
    assert pdf_bytes.startswith(b"%PDF"), "PDF must start with %PDF header"

    # Assert minimum size (realistic threshold for a simple rack PDF)
    assert len(pdf_bytes) > 5000, f"PDF too small: {len(pdf_bytes)} bytes"

    # Assert PDF EOF marker present
    assert b"%%EOF" in pdf_bytes, "PDF must contain %%EOF marker"


def test_patchbook_pdf_contains_rack_metadata(
    db_session: Session, sample_rack_basic: Rack
):
    """Test that PDF contains rack name and metadata."""
    pdf_bytes = build_patchbook_pdf_bytes(db_session, sample_rack_basic)
    pdf_str = pdf_bytes.decode("latin-1", errors="ignore")

    # Check for rack name
    assert sample_rack_basic.name in pdf_str, "PDF must contain rack name"

    # Check for template version
    assert PATCHBOOK_TEMPLATE_VERSION in pdf_str, "PDF must contain template version"

    # Check for PatchHive branding
    assert "PatchHive" in pdf_str, "PDF must contain PatchHive branding"


def test_patchbook_pdf_deterministic_with_same_timestamp(
    db_session: Session, sample_rack_basic: Rack
):
    """Test that same rack + timestamp produces identical PDF bytes."""
    fixed_timestamp = datetime(2024, 1, 15, 10, 30, 0)

    pdf_bytes_1 = build_patchbook_pdf_bytes(
        db_session, sample_rack_basic, export_timestamp=fixed_timestamp
    )
    pdf_bytes_2 = build_patchbook_pdf_bytes(
        db_session, sample_rack_basic, export_timestamp=fixed_timestamp
    )

    # Exact byte-for-byte match (deterministic)
    assert pdf_bytes_1 == pdf_bytes_2, "PDFs must be deterministic with same inputs"

    # Hash verification
    hash_1 = sha256(pdf_bytes_1).hexdigest()
    hash_2 = sha256(pdf_bytes_2).hexdigest()
    assert hash_1 == hash_2, "PDF hashes must match for same inputs"


def test_patchbook_pdf_with_patches_includes_patch_info(
    db_session: Session, sample_rack_basic: Rack, sample_user
):
    """Test that PDF includes patch information when patches exist."""
    # Add a patch to the rack
    patch = Patch(
        user_id=sample_user.id,
        rack_id=sample_rack_basic.id,
        name="Test Patch Alpha",
        category="Tonal",
        description="A test patch for PDF export",
        connections=[
            {"from_module": 1, "to_module": 2, "from_port": "Out", "to_port": "In"}
        ],
        generation_seed=42,
        generation_version="1.0.0",
    )
    db_session.add(patch)
    db_session.commit()

    pdf_bytes = build_patchbook_pdf_bytes(db_session, sample_rack_basic)
    pdf_str = pdf_bytes.decode("latin-1", errors="ignore")

    # Check for patch name
    assert "Test Patch Alpha" in pdf_str, "PDF must contain patch name"

    # Check for category
    assert "Tonal" in pdf_str, "PDF must contain patch category"


def test_patchbook_pdf_sorts_patches_deterministically(
    db_session: Session, sample_rack_basic: Rack, sample_user
):
    """Test that patches are sorted by ID for determinism."""
    # Add patches in reverse order
    patches = [
        Patch(
            user_id=sample_user.id,
            rack_id=sample_rack_basic.id,
            name=f"Patch {letter}",
            category="Tonal",
            connections=[],
            generation_seed=i,
            generation_version="1.0.0",
        )
        for i, letter in enumerate(["Z", "M", "A"])
    ]
    for patch in patches:
        db_session.add(patch)
    db_session.commit()

    # Refresh to get IDs
    db_session.refresh(sample_rack_basic)

    pdf_bytes = build_patchbook_pdf_bytes(db_session, sample_rack_basic)
    pdf_str = pdf_bytes.decode("latin-1", errors="ignore")

    # Find positions of patch names in PDF
    pos_z = pdf_str.find("Patch Z")
    pos_m = pdf_str.find("Patch M")
    pos_a = pdf_str.find("Patch A")

    # Patches should appear in ID order (Z, M, A insertion order)
    # Since IDs are sequential, insertion order = ID order
    assert pos_z < pos_m < pos_a, "Patches must be sorted by ID in PDF"


def test_compute_patchbook_content_hash_deterministic():
    """Test that content hash is deterministic for same inputs."""
    rack_id = 123
    patch_ids = [5, 3, 1, 4, 2]  # Unsorted on purpose

    hash_1 = compute_patchbook_content_hash(rack_id, patch_ids)
    hash_2 = compute_patchbook_content_hash(rack_id, patch_ids)

    assert hash_1 == hash_2, "Content hash must be deterministic"
    assert len(hash_1) == 64, "SHA256 hash must be 64 hex chars"


def test_compute_patchbook_content_hash_sorts_patches():
    """Test that content hash sorts patch IDs before hashing."""
    rack_id = 123
    patch_ids_unsorted = [5, 3, 1, 4, 2]
    patch_ids_sorted = [1, 2, 3, 4, 5]

    hash_unsorted = compute_patchbook_content_hash(rack_id, patch_ids_unsorted)
    hash_sorted = compute_patchbook_content_hash(rack_id, patch_ids_sorted)

    assert hash_unsorted == hash_sorted, "Hash must be same regardless of input order"


def test_compute_patchbook_content_hash_changes_with_template():
    """Test that hash changes when template version changes (theoretical)."""
    # This test documents the contract: if template version changes,
    # hash MUST change (enforced by including version in hash)
    rack_id = 123
    patch_ids = [1, 2, 3]

    current_hash = compute_patchbook_content_hash(rack_id, patch_ids)

    # Simulate different template by checking hash input
    # (we can't actually change PATCHBOOK_TEMPLATE_VERSION in runtime)
    assert PATCHBOOK_TEMPLATE_VERSION in str(current_hash), "Hash must depend on template version"


def test_patchbook_pdf_includes_timestamp_normalization(
    db_session: Session, sample_rack_basic: Rack
):
    """Test that PDF embeds the provided timestamp, not current time."""
    fixed_timestamp = datetime(2024, 6, 15, 14, 30, 0)

    pdf_bytes = build_patchbook_pdf_bytes(
        db_session, sample_rack_basic, export_timestamp=fixed_timestamp
    )
    pdf_str = pdf_bytes.decode("latin-1", errors="ignore")

    # Check that fixed timestamp appears in PDF
    assert "2024-06-15 14:30" in pdf_str, "PDF must embed the provided timestamp"


def test_patchbook_pdf_minimum_content_threshold(
    db_session: Session, sample_rack_basic: Rack, sample_user
):
    """Test that PDF with multiple patches exceeds realistic size threshold."""
    # Add 5 patches
    for i in range(5):
        patch = Patch(
            user_id=sample_user.id,
            rack_id=sample_rack_basic.id,
            name=f"Patch {i}",
            category="Tonal",
            description=f"Description for patch {i}",
            connections=[],
            generation_seed=i,
            generation_version="1.0.0",
        )
        db_session.add(patch)
    db_session.commit()

    pdf_bytes = build_patchbook_pdf_bytes(db_session, sample_rack_basic)

    # With 5 patches, expect at least 10KB
    assert len(pdf_bytes) > 10_000, f"PDF with 5 patches too small: {len(pdf_bytes)} bytes"
