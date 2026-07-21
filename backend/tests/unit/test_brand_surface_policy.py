from export.patchbook.design.brand_policy import (
    CYBER_HIVE_AMBER,
    PDF_CREATOR_PATTERN,
    scan_forbidden_strings,
    validate_brand_marks,
)
from export.patchbook.design.layout_ir import BrandMarkRef, LayoutRegion, PageKind, PatchPageLayoutIR


def test_forbidden_aal_product_language() -> None:
    result = scan_forbidden_strings(["This is an AAL product"])
    assert result.ok is False


def test_zero_state_footer_mark_ok() -> None:
    page = PatchPageLayoutIR(
        page_id="p1",
        page_index=0,
        page_kind=PageKind.FRONT_MATTER,
        page_size="us_letter",
        regions=(
            LayoutRegion(
                region_id="identity",
                role="identity",
                required=True,
                bbox_pt=(36.0, 700.0, 100.0, 20.0),
                reading_order=0,
            ),
        ),
        reading_order=("identity",),
        brand_marks=(
            BrandMarkRef(
                mark_id="zero_state",
                page_role="footer",
                bbox_pt=(36.0, 24.0, 60.0, 6.0),
                opacity=0.5,
            ),
        ),
    )
    result = validate_brand_marks([page])
    assert result.ok is True
    assert CYBER_HIVE_AMBER.startswith("#")
    assert "Zero State" in PDF_CREATOR_PATTERN
