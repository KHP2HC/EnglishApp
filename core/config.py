"""Centralized configuration for EnglishCoach Pro.

All configuration is sourced from environment variables.
No credentials are hard-coded, printed, or committed.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────
    ENVIRONMENT: str = "development"

    # ── API ──────────────────────────────────────────────
    API_PORT: int = 8000

    # ── CORS ─────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    CORS_ORIGINS: str = (
        "http://localhost:5173," "http://localhost:4173," "http://localhost:8000"
    )

    # ── Supabase ─────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ── JWT ──────────────────────────────────────────────
    # Supabase uses HS256 by default with the project's JWT secret.
    # Set this to your Supabase project's JWT secret for verification.
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "authenticated"

    # ── Rate Limiting ────────────────────────────────────
    # Requests per window per IP for sensitive endpoints.
    RATE_LIMIT_AUTH_REQUESTS: int = 10
    RATE_LIMIT_AUTH_WINDOW_SECONDS: int = 60
    RATE_LIMIT_DEFAULT_REQUESTS: int = 100
    RATE_LIMIT_DEFAULT_WINDOW_SECONDS: int = 60

    # ── Database (current SQLite path; future PostgreSQL) ──
    DATABASE_URL: str = ""

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ──────────────────────────────────────────────────────
    # Validators
    # ──────────────────────────────────────────────────────

    @field_validator("ENVIRONMENT")
    @classmethod
    def _validate_environment(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("development", "staging", "production"):
            return "development"
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        v = v.upper().strip()
        allowed = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        return v if v in allowed else "INFO"

    # ──────────────────────────────────────────────────────
    # Computed properties
    # ──────────────────────────────────────────────────────

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list of stripped origin strings."""
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def sqlite_url(self) -> str:
        """Fallback SQLite database URL for local development."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")
        return f"sqlite:///{db_file}"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


def reload_settings() -> Settings:
    """Force-reload settings (useful in tests)."""
    get_settings.cache_clear()
    return get_settings()
