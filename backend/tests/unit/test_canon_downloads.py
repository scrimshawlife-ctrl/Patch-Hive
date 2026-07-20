"""Tests for short-lived, resource-scoped export download grants."""

import pytest

from canon.downloads import DownloadTokenError, issue_download_token, verify_download_token

SECRET = "test-only-download-secret-with-32-bytes-minimum"


def test_download_token_is_scoped_and_expires() -> None:
    token = issue_download_token(
        export_id="export-1", user_id="user-1", secret=SECRET, now=1_000, ttl_seconds=60
    )
    grant = verify_download_token(
        token, export_id="export-1", user_id="user-1", secret=SECRET, now=1_060
    )
    assert grant.expires_at == 1_060

    with pytest.raises(DownloadTokenError, match="expired"):
        verify_download_token(
            token, export_id="export-1", user_id="user-1", secret=SECRET, now=1_061
        )


@pytest.mark.parametrize(
    ("export_id", "user_id"),
    [("export-2", "user-1"), ("export-1", "user-2")],
)
def test_download_token_rejects_cross_scope_use(export_id: str, user_id: str) -> None:
    token = issue_download_token(export_id="export-1", user_id="user-1", secret=SECRET, now=1_000)
    with pytest.raises(DownloadTokenError, match="scope mismatch"):
        verify_download_token(token, export_id=export_id, user_id=user_id, secret=SECRET, now=1_001)


def test_download_token_rejects_tampering() -> None:
    token = issue_download_token(export_id="export-1", user_id="user-1", secret=SECRET, now=1_000)
    version, payload, signature = token.split(".")
    replacement = "0" if signature[-1] != "0" else "1"
    tampered = f"{version}.{payload}.{signature[:-1]}{replacement}"
    with pytest.raises(DownloadTokenError, match="signature"):
        verify_download_token(
            tampered, export_id="export-1", user_id="user-1", secret=SECRET, now=1_001
        )
