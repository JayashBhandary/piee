"""
PIEE — Application Configuration

Centralized settings loaded from environment variables.
Supports both local and cloud deployment modes.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class DeploymentMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


class Settings(BaseSettings):
    """Application-wide settings, sourced from environment variables."""

    # ── Deployment ──────────────────────────────
    deployment_mode: DeploymentMode = Field(
        default=DeploymentMode.LOCAL,
        description="Run as 'local' (OSS) or 'cloud' (SaaS)",
    )

    # ── Database ────────────────────────────────
    database_url: str = Field(
        default="file:./dev.db",
        description="Prisma-compatible database URL",
    )

    # ── Security ────────────────────────────────
    jwt_secret: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT signing",
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 hours

    encryption_key: str = Field(
        default="",
        description="Fernet key for encrypting provider API keys at rest",
    )

    # ── Server ──────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # ── Provider Bootstrap ──────────────────────
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # ── Feature Flag Overrides ──────────────────
    billing_enabled: Optional[bool] = None
    usage_limits_enabled: Optional[bool] = None
    premium_models_enabled: Optional[bool] = None
    admin_dashboard_enabled: Optional[bool] = None

    @property
    def is_cloud(self) -> bool:
        return self.deployment_mode == DeploymentMode.CLOUD

    @property
    def is_local(self) -> bool:
        return self.deployment_mode == DeploymentMode.LOCAL

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    return Settings()
