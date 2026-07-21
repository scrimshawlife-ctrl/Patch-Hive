"""Publication / artistic dual-artifact compose tests."""

from __future__ import annotations

from pathlib import Path

from export.patchbook.design.content_spine import LoadedLibrary, LoadedLibraryItem
from export.patchbook.design.engine import compose_design_export_pack
from export.patchbook.design.layout_ir import PageKind
from export.patchbook.design.recipe import (
    BookProfile,
    OutputProfile,
    PatchBookMode,
    ResolvedStyleRecipe,
    StyleConstraints,
    StyleWeights,
    TemplateFamilyId,
)
from export.patchbook.design.content_spine import seal_orm_patch_to_compilation
from patches.models import Patch


def _minimal_library() -> LoadedLibrary:
    patch = Patch(
        id=1,
        rack_id=1,
        run_id=1,
        name="Plate Patch",
        category="Voice",
        description="Artistic dual-artifact fixture",
        connections=[
            {
                "from_module_id": 1,
                "from_port": "Out",
                "to_module_id": 2,
                "to_port": "In",
                "cable_type": "audio",
            }
        ],
        generation_seed=9,
        generation_version="1.0.0",
    )
    compilation = seal_orm_patch_to_compilation(
        patch,
        source_run_id="gen-run-1-aaaaaaaaaaaaaaaa",
        source_rig_revision_id="rig-rev-" + "a" * 32,
        rig_snapshot={"modules": []},
        position=0,
    )
    item = LoadedLibraryItem(position=0, compilation=compilation, orm_patch_id=1)
    from export.patchbook.design.content_spine import library_content_hash

    return LoadedLibrary(
        source_run_id="gen-run-1-aaaaaaaaaaaaaaaa",
        source_rig_revision_id="rig-rev-" + "a" * 32,
        bridge_artifact_manifest_hash="b" * 64,
        library_content_hash=library_content_hash([item]),
        load_path="compile_on_export",
        items=(item,),
    )


def test_plate_family_publication_emits_plate_and_appendix(tmp_path: Path) -> None:
    recipe = ResolvedStyleRecipe(
        mode=PatchBookMode.GALLERY,
        template_family=TemplateFamilyId.IMPOSSIBLE_INSTRUMENT,
        template_family_version="1.0.0",
        seed=1,
        weights=StyleWeights(legibility=15, diagram_literalness=10),
        constraints=StyleConstraints(
            book_profile=BookProfile.PUBLICATION,
            canonical_appendix_required=True,
            artistic_disclosure_acknowledged=True,
        ),
        output_profile=OutputProfile.PRINT_PDF,
        resolved_tier="studio",
        zero_state_brand_cap=6,
    )
    library = _minimal_library()
    result = compose_design_export_pack(
        library, recipe, out_dir=tmp_path / "pack", export_id="export-art-1"
    )
    kinds = [p.page_kind for p in result.layout_irs]
    assert PageKind.PLATE in kinds
    assert PageKind.APPENDIX_EXECUTION in kinds
    assert (tmp_path / "pack" / "technical" / "PatchBook-execution.pdf").exists()
    assert (tmp_path / "pack" / "PatchBook.pdf").exists()
    assert any((tmp_path / "pack" / "pages" / "json").glob("*-plate.json"))
    assert any((tmp_path / "pack" / "pages" / "json").glob("*-appendix.json"))
