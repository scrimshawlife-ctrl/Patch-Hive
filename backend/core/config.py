"""
Core configuration for PatchHive backend.
Uses pydantic-settings for environment-based configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "PatchHive"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://patchhive:patchhive@localhost:5432/patchhive"
    database_echo: bool = False

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Patch Engine
    patch_engine_version: str = "1.0.0"
    max_patches_per_generation: int = 20
    default_generation_seed: int = 42

    # File Storage
    export_dir: str = "./exports"
    waveform_dir: str = "./waveforms"

    # ABX-Core / SEED
    abx_core_version: str = "1.3"
    enforce_seed_traceability: bool = True

    # Git tracking (optional, for provenance)
    git_commit: str = ""  # Set by environment or CI/CD


# Global settings instance
settings = Settings()
