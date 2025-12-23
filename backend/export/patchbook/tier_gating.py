"""Tier gating logic for PatchBook features."""

from __future__ import annotations

from .models import PatchBookTier


class TierFeatures:
    """Feature flags for each tier."""

    def __init__(self, tier: PatchBookTier):
        self.tier = tier

    # Page-level computed panels
    @property
    def patch_fingerprint(self) -> bool:
        """Patch fingerprint available in Core+."""
        return self.tier in {
            PatchBookTier.CORE,
            PatchBookTier.PRO,
            PatchBookTier.STUDIO,
        }

    @property
    def stability_envelope(self) -> bool:
        """Stability envelope available in Core+."""
        return self.tier in {
            PatchBookTier.CORE,
            PatchBookTier.PRO,
            PatchBookTier.STUDIO,
        }

    @property
    def troubleshooting_tree(self) -> bool:
        """Troubleshooting tree available in Core+."""
        return self.tier in {
            PatchBookTier.CORE,
            PatchBookTier.PRO,
            PatchBookTier.STUDIO,
        }

    @property
    def performance_macros(self) -> bool:
        """Performance macros available in Core+."""
        return self.tier in {
            PatchBookTier.CORE,
            PatchBookTier.PRO,
            PatchBookTier.STUDIO,
        }

    @property
    def computed_variants(self) -> bool:
        """Computed variants available in Pro+."""
        return self.tier in {PatchBookTier.PRO, PatchBookTier.STUDIO}

    # Book-level analytics
    @property
    def golden_rack_analysis(self) -> bool:
        """Golden rack analysis available in Pro+."""
        return self.tier in {PatchBookTier.PRO, PatchBookTier.STUDIO}

    @property
    def compatibility_report(self) -> bool:
        """Compatibility report available in Pro+."""
        return self.tier in {PatchBookTier.PRO, PatchBookTier.STUDIO}

    @property
    def learning_path(self) -> bool:
        """Learning path available in Pro+."""
        return self.tier in {PatchBookTier.PRO, PatchBookTier.STUDIO}

    # Document features
    @property
    def watermarked(self) -> bool:
        """Free tier is watermarked."""
        return self.tier == PatchBookTier.FREE

    @property
    def full_patching_order(self) -> bool:
        """Full patching order (not minimal) in Core+."""
        return self.tier in {
            PatchBookTier.CORE,
            PatchBookTier.PRO,
            PatchBookTier.STUDIO,
        }

    def get_tier_label(self) -> str:
        """Get human-readable tier label."""
        labels = {
            PatchBookTier.FREE: "Free Preview",
            PatchBookTier.CORE: "PatchBook Core",
            PatchBookTier.PRO: "PatchBook Pro",
            PatchBookTier.STUDIO: "PatchBook Studio",
        }
        return labels.get(self.tier, "Unknown")


def should_include_computed_panels(tier: PatchBookTier) -> bool:
    """Check if tier includes any computed panels."""
    features = TierFeatures(tier)
    return (
        features.patch_fingerprint
        or features.stability_envelope
        or features.troubleshooting_tree
        or features.performance_macros
        or features.computed_variants
    )


def should_include_book_analytics(tier: PatchBookTier) -> bool:
    """Check if tier includes book-level analytics."""
    features = TierFeatures(tier)
    return (
        features.golden_rack_analysis
        or features.compatibility_report
        or features.learning_path
    )
