from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from patchhive.ops.generate_patch import generate_patch
from patchhive.schemas import FieldMeta, FieldStatus, PatchIntent, Provenance, ProvenanceType
from patchhive.schemas_library import (
    PatchCard,
    PatchCategory,
    PatchDifficulty,
    PatchEnvelope,
    PatchLibrary,
    PatchLibraryItem,
)


@dataclass(frozen=True)
class LibraryBuildSpec:
    total: int = 24


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _intent(canon_id: str, archetype: str, seed: int) -> PatchIntent:
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{canon_id}:seed:{seed}",
                method="run_library.v1",
            )
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )
    return PatchIntent(archetype=archetype, energy="focused", focus="clarity", meta=meta)


def _category_for(archetype: str) -> PatchCategory:
    return {
        "basic_voice": PatchCategory.Voice,
        "generative_mod": PatchCategory.Generative,
        "clocked_sequence": PatchCategory.ClockRhythm,
    }.get(archetype, PatchCategory.Study)


def _difficulty_for(archetype: str) -> PatchDifficulty:
    return {
        "basic_voice": PatchDifficulty.Beginner,
        "clocked_sequence": PatchDifficulty.Intermediate,
        "generative_mod": PatchDifficulty.Advanced,
    }.get(archetype, PatchDifficulty.Experimental)


def _card_name(archetype: str, index: int) -> str:
    return f"{archetype.replace('_', ' ').title()} {index:02d}"


def run_library(
    canon,
    *,
    constraints,
    include_diagrams: bool = False,
    build_spec: LibraryBuildSpec = LibraryBuildSpec(),
) -> PatchLibrary:
    # TODO: Integrate template-based generation using build_registry_for_rig(canon)
    # from patchhive.templates.build_registry import build_registry_for_rig
    # reg = build_registry_for_rig(canon)
    # Use reg.templates to drive patch generation with VL2 micro-grammar when detected

    archetypes = ["basic_voice", "generative_mod", "clocked_sequence"]
    items: List[PatchLibraryItem] = []

    for i in range(build_spec.total):
        archetype = archetypes[i % len(archetypes)]
        intent = _intent(canon.rig_id, archetype, i)
        payload = generate_patch(canon, intent=intent, seed=i)
        patch = payload["patch"]
        plan = payload["plan"]
        validation = payload["validation"]

        card = PatchCard(
            patch_id=patch.patch_id,
            name=_card_name(archetype, i + 1),
            category=_category_for(archetype),
            difficulty=_difficulty_for(archetype),
            cable_count=len(patch.cables),
            stability_score=float(validation.stability_score),
            tags=[archetype],
            warnings=plan.warnings + validation.silence_risk + validation.runaway_risk,
            rationale=f"tmpl.{archetype}: run_library.v1",
        )

        envelope = PatchEnvelope(closure_strength=float(validation.stability_score))

        items.append(
            PatchLibraryItem(
                patch=patch,
                plan=plan,
                validation=validation,
                card=card,
                envelope=envelope,
            )
        )

    return PatchLibrary(patches=items, constraints=constraints)
