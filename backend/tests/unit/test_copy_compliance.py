"""Copy compliance tests for dashboard and referral text."""

from pathlib import Path
import re


def test_dashboard_copy_compliance():
    """Ensure required copy is present and forbidden terms absent."""
    account_path = Path(__file__).resolve().parents[3] / "frontend/src/pages/Account.tsx"
    content = account_path.read_text(encoding="utf-8")

    required_lines = [
        "PatchHive is free to explore. You only pay when you export something you want to keep.",
        "You’ll receive free credits if your friend makes their first purchase.",
    ]
    for line in required_lines:
        assert line in content

    forbidden_terms = ["upgrade", "premium", "pro", "subscribe", "commission", "affiliate"]
    lowered = content.lower()
    for term in forbidden_terms:
        assert re.search(rf"\b{re.escape(term)}\b", lowered) is None
