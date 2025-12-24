"""PatchBook tier feature gating."""

from __future__ import annotations

from dataclasses import dataclass

from .models import PatchBookTier


@dataclass(frozen=True)
class PatchBookTierFeatures:
    patch_fingerprint: bool
    stability_envelope: bool
    troubleshooting_tree: bool
    performance_macros: bool
    patch_variants: bool
    golden_rack_arrangement: bool
    compatibility_report: bool
    learning_path: bool
    rack_fit_score: bool


TIER_FEATURES = {
    PatchBookTier.FREE: PatchBookTierFeatures(
        patch_fingerprint=False,
        stability_envelope=False,
        troubleshooting_tree=False,
        performance_macros=False,
        patch_variants=False,
        golden_rack_arrangement=False,
        compatibility_report=False,
        learning_path=False,
        rack_fit_score=False,
    ),
    PatchBookTier.CORE: PatchBookTierFeatures(
        patch_fingerprint=True,
        stability_envelope=True,
        troubleshooting_tree=True,
        performance_macros=True,
        patch_variants=False,
        golden_rack_arrangement=False,
        compatibility_report=False,
        learning_path=False,
        rack_fit_score=False,
    ),
    PatchBookTier.PRO: PatchBookTierFeatures(
        patch_fingerprint=True,
        stability_envelope=True,
        troubleshooting_tree=True,
        performance_macros=True,
        patch_variants=True,
        golden_rack_arrangement=True,
        compatibility_report=True,
        learning_path=True,
        rack_fit_score=True,
    ),
    PatchBookTier.STUDIO: PatchBookTierFeatures(
        patch_fingerprint=True,
        stability_envelope=True,
        troubleshooting_tree=True,
        performance_macros=True,
        patch_variants=True,
        golden_rack_arrangement=True,
        compatibility_report=True,
        learning_path=True,
        rack_fit_score=True,
    ),
}


def get_tier_features(tier: PatchBookTier) -> PatchBookTierFeatures:
    return TIER_FEATURES[tier]
