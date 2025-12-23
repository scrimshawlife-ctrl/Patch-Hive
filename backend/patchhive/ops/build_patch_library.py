from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from patchhive.ops.derive_symbolic_envelope import derive_symbolic_envelope
from patchhive.ops.generate_patch_candidates import (
    _build_patch_from_assignment,
    _enumerate_assignments,
    _jack_role_candidates,
)
from patchhive.ops.name_patch import categorize_patch, difficulty_from_cables, name_patch
from patchhive.ops.validate_patch import validate_patch
from patchhive.schemas import (
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    PatchIntent,
    PatchPlan,
    Provenance,
    ProvenanceType,
)
from patchhive.schemas_library import (
    PatchCard,
    PatchLibrary,
    PatchLibraryItem,
    PatchSpaceConstraints,
)
from patchhive.templates.registry import PatchTemplateRegistry


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(rig_id: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{rig_id}",
                method="build_patch_library.v1",
            )
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )


def _ritual_perform_steps() -> List[str]:
    return [
        "Begin in silence; introduce the primary signal path.",
        "Increase modulation depth only after the core path is stable.",
        "Seal by reducing complexity and returning to a steady output.",
    ]


def _novelty_signature(patch) -> str:
    items = []
    for cable in patch.cables:
        items.append(f"{cable.type.value}:{cable.from_jack}->{cable.to_jack}")
    return "|".join(sorted(items))


def _novelty_score(sig: str) -> float:
    h = int(__import__("hashlib").sha256(sig.encode("utf-8")).hexdigest()[:8], 16)
    return (h % 1000) / 1000.0


def build_patch_plan(intent: PatchIntent, patch_id: str) -> PatchPlan:
    meta = intent.meta
    return PatchPlan(
        patch_id=patch_id,
        intent=intent,
        setup=[
            "Confirm semi-normalled routes and decide which will remain intact.",
            "Set macro intensity to minimum; bring volume up last.",
            "Verify monitoring/output chain before increasing levels.",
        ],
        perform=_ritual_perform_steps(),
        warnings=[
            "If silent: confirm audio path + output monitoring.",
            "If unstable: reduce modulation depth and reintroduce slowly.",
        ],
        why_it_works=[
            "Template-first design ensures musical coherence and repeatable learning.",
            "Ritual timing enforces closure (seal) and reduces runaway complexity.",
        ],
        meta=meta,
    )


def build_patch_library(
    canon: CanonicalRig,
    *,
    registry: PatchTemplateRegistry,
    constraints: PatchSpaceConstraints,
    seed_base: int = 100,
) -> PatchLibrary:
    role_buckets = _jack_role_candidates(canon)

    items: List[PatchLibraryItem] = []
    meta = _meta_derived(canon.rig_id)

    for template in registry.all():
        if len(template.slots) > constraints.max_cables:
            continue

        assigns = _enumerate_assignments(
            template,
            role_buckets,
            max_candidates=constraints.max_candidates_per_template,
        )

        candidates = []
        for idx, assignment in enumerate(assigns):
            seed = seed_base + idx
            patch = _build_patch_from_assignment(canon, template, assignment, seed=seed)

            intent = PatchIntent(
                archetype=template.archetype,
                energy="medium",
                focus="learnability",
                meta=meta,
            )
            plan = build_patch_plan(intent, patch.patch_id)
            validation = validate_patch(patch, plan)
            envelope = derive_symbolic_envelope(patch, plan)

            if constraints.require_output_path and validation.silence_risk:
                if template.category != "Utility / Calibration":
                    continue

            candidates.append((patch, plan, validation, envelope, assignment))

            if len(candidates) >= constraints.keep_top_per_template:
                break

        seen = set()
        curated = []
        for patch, plan, validation, envelope, assignment in candidates:
            sig = _novelty_signature(patch)
            if sig in seen:
                continue
            seen.add(sig)
            curated.append((patch, plan, validation, envelope, sig))

        curated.sort(
            key=lambda x: (
                -x[2].stability_score,
                -x[3].closure_strength,
                len(x[0].cables),
                x[0].patch_id,
            )
        )

        for patch, plan, validation, envelope, sig in curated[: constraints.keep_top_per_template]:
            tags = list(template.tags)
            cat = categorize_patch(template.archetype)
            diff = difficulty_from_cables(len(patch.cables), feedback=bool(validation.runaway_risk))
            nm = name_patch(template.archetype, patch, tags)

            card = PatchCard(
                patch_id=patch.patch_id,
                name=nm,
                category=cat,
                difficulty=diff,
                tags=tags,
                archetype=template.archetype,
                cable_count=len(patch.cables),
                stability_score=validation.stability_score,
                novelty_score=_novelty_score(sig),
                warnings=list(validation.warnings),
                rationale=(
                    f"{template.template_id}: template-filled exhaustive candidate within bounded patch space."
                ),
            )

            items.append(
                PatchLibraryItem(
                    card=card,
                    patch=patch,
                    plan=plan,
                    validation=validation,
                    envelope=envelope,
                    diagram=None,
                )
            )

    items.sort(
        key=lambda it: (
            it.card.category.value,
            it.card.difficulty.value,
            -it.card.stability_score,
            it.card.cable_count,
            it.card.patch_id,
        )
    )

    return PatchLibrary(
        rig_id=canon.rig_id,
        generated_at=_now_utc(),
        constraints=constraints,
        patches=items,
    )
