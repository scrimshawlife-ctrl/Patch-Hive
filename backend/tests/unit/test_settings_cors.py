"""Settings / env parsing unit tests."""

from core.config import Settings


def test_cors_origins_accepts_comma_separated_env(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://localhost",
    )
    settings = Settings()
    assert settings.cors_origins == [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ]


def test_cors_origins_accepts_json_list_env(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        '["http://a.example","http://b.example"]',
    )
    settings = Settings()
    assert settings.cors_origins == ["http://a.example", "http://b.example"]
