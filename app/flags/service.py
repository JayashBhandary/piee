"""
PIEE — Feature Flag Service

Runtime feature flag system that combines:
  1. Deployment mode defaults (local vs cloud)
  2. Database overrides (FeatureFlag table)
  3. Environment variable overrides

Priority: env override > DB override > deployment mode default
"""

from __future__ import annotations

from typing import Dict, Optional

from app.config import Settings, DeploymentMode


# ── Default Flag Definitions ───────────────────

DEFAULT_FLAGS: Dict[str, Dict[str, bool]] = {
    "billing_enabled": {"local": False, "cloud": True},
    "usage_limits_enabled": {"local": False, "cloud": True},
    "premium_models_enabled": {"local": False, "cloud": True},
    "admin_dashboard_enabled": {"local": True, "cloud": True},
    "audit_logging_enabled": {"local": True, "cloud": True},
    "api_key_auth_enabled": {"local": True, "cloud": True},
    "credit_wallet_enabled": {"local": False, "cloud": True},
    "rate_limiting_enabled": {"local": False, "cloud": True},
}


class FeatureFlagService:
    """Evaluates feature flags with multi-layer override logic."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._mode = settings.deployment_mode.value  # "local" or "cloud"

    async def is_enabled(self, flag_key: str) -> bool:
        """
        Check if a feature flag is enabled.
        Priority: env override > DB override > deployment default.
        """
        # 1. Check environment variable override
        env_override = self._get_env_override(flag_key)
        if env_override is not None:
            return env_override

        # 2. Check database override
        db_override = await self._get_db_override(flag_key)
        if db_override is not None:
            return db_override

        # 3. Fall back to deployment mode default
        return self._get_default(flag_key)

    async def get_all_flags(self) -> Dict[str, bool]:
        """Return the resolved value of all known flags."""
        result = {}
        for key in DEFAULT_FLAGS:
            result[key] = await self.is_enabled(key)
        return result

    async def set_flag(self, flag_key: str, value: bool) -> None:
        """Persist a flag override in the database."""
        from prisma import Prisma

        db = Prisma()
        await db.connect()
        try:
            existing = await db.featureflag.find_unique(where={"key": flag_key})
            if existing:
                await db.featureflag.update(
                    where={"key": flag_key},
                    data={"value": value},
                )
            else:
                defaults = DEFAULT_FLAGS.get(flag_key, {"local": False, "cloud": False})
                await db.featureflag.create(
                    data={
                        "key": flag_key,
                        "value": value,
                        "description": f"Feature flag: {flag_key}",
                        "localDefault": defaults["local"],
                        "cloudDefault": defaults["cloud"],
                    }
                )
        finally:
            await db.disconnect()

    # ── Internal Helpers ───────────────────────

    def _get_env_override(self, flag_key: str) -> Optional[bool]:
        """Check if the settings has an env override for this flag."""
        attr = getattr(self.settings, flag_key, None)
        return attr  # None means no override

    def _get_default(self, flag_key: str) -> bool:
        """Get default value for current deployment mode."""
        flag_def = DEFAULT_FLAGS.get(flag_key)
        if not flag_def:
            return False
        return flag_def.get(self._mode, False)

    async def _get_db_override(self, flag_key: str) -> Optional[bool]:
        """Check database for a flag override."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                record = await db.featureflag.find_unique(where={"key": flag_key})
                if record:
                    return record.value
                return None
            finally:
                await db.disconnect()
        except Exception:
            return None  # DB not available — fall through to default
