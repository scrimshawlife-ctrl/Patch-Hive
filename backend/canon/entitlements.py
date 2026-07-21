"""Server-side tier / Design Engine entitlements (KD-5, KD-18).

No client-supplied tier. Until a real subscription model exists, resolve a
single default tier (core) with optional admin/feature-map override.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.config import settings
from export.patchbook.design.recipe import TemplateFamilyId

TierName = Literal["free", "core", "pro", "studio"]

# Family floor table from design §D
_FAMILY_TIER_FLOOR: dict[TemplateFamilyId, TierName] = {
    TemplateFamilyId.SIGNAL_MANUAL: "free",
    TemplateFamilyId.MODULAR_FIELD_NOTES: "free",
    TemplateFamilyId.CIRCUIT_ARCHIVE: "free",
    TemplateFamilyId.HIVE_SYSTEMS_ATLAS: "core",
    TemplateFamilyId.OPEN_STATE: "core",
    TemplateFamilyId.OSCILLOSCOPE_JOURNAL: "core",
    TemplateFamilyId.PATENT_FUTURE: "core",
    TemplateFamilyId.MUSEUM_OF_SIGNAL: "pro",
    TemplateFamilyId.PATCH_CARTOGRAPHY: "pro",
    TemplateFamilyId.SONIC_BRUTALISM: "pro",
    TemplateFamilyId.RITUAL_MACHINE: "studio",
    TemplateFamilyId.IMPOSSIBLE_INSTRUMENT: "studio",
}

_TIER_RANK: dict[TierName, int] = {"free": 0, "core": 1, "pro": 2, "studio": 3}


@dataclass(frozen=True)
class DesignEntitlements:
    tier: TierName
    design_engine_enabled: bool
    fulfillment_enabled: bool
    publication_enabled: bool
    allowed_families: frozenset[TemplateFamilyId]


def resolve_user_tier(user_id: int) -> TierName:
    """Resolve presentation tier for a user. Client cannot override."""
    _ = user_id  # reserved for future entitlement table
    override = (settings.design_engine_default_tier or "core").lower().strip()
    if override not in _TIER_RANK:
        return "core"
    return override  # type: ignore[return-value]


def tier_allows_family(tier: TierName, family: TemplateFamilyId) -> bool:
    floor = _FAMILY_TIER_FLOOR.get(family, "studio")
    return _TIER_RANK[tier] >= _TIER_RANK[floor]


def allowed_families_for_tier(tier: TierName) -> frozenset[TemplateFamilyId]:
    return frozenset(f for f in TemplateFamilyId if tier_allows_family(tier, f))


def get_design_entitlements(user_id: int) -> DesignEntitlements:
    tier = resolve_user_tier(user_id)
    return DesignEntitlements(
        tier=tier,
        design_engine_enabled=bool(settings.enable_patchbook_design_engine),
        fulfillment_enabled=bool(settings.enable_canon_export_fulfillment),
        publication_enabled=bool(settings.enable_patchbook_publication_profile),
        allowed_families=allowed_families_for_tier(tier),
    )
