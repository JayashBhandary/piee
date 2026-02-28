"""
PIEE — Shared FastAPI Dependencies

Provides dependency injection for database access, authentication,
and feature flag checking across all endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader

from app.config import Settings, get_settings

# ── Security Schemes ───────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ── Database ───────────────────────────────────

async def get_db():
    """Yield a Prisma client instance."""
    from prisma import Prisma

    db = Prisma()
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()


# ── Authentication ─────────────────────────────

async def get_current_user(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    settings: Settings = Depends(get_settings),
):
    """
    Resolve the current user from either:
      1. Bearer JWT token
      2. X-API-Key header
    """
    from app.auth.service import AuthService

    auth_service = AuthService(settings)

    # Try Bearer token first
    if bearer and bearer.credentials:
        user = await auth_service.verify_jwt(bearer.credentials)
        if user:
            return user

    # Try API key
    if api_key:
        user = await auth_service.verify_api_key(api_key)
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide a valid Bearer token or X-API-Key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    settings: Settings = Depends(get_settings),
):
    """Same as get_current_user but returns None instead of raising."""
    from app.auth.service import AuthService

    auth_service = AuthService(settings)

    if bearer and bearer.credentials:
        user = await auth_service.verify_jwt(bearer.credentials)
        if user:
            return user
    if api_key:
        user = await auth_service.verify_api_key(api_key)
        if user:
            return user
    return None


# ── Feature Flags ──────────────────────────────

async def require_feature(flag_key: str):
    """
    Factory for feature-flag dependency.
    Usage: Depends(require_feature("billing_enabled"))
    """

    async def _check(settings: Settings = Depends(get_settings)):
        from app.flags.service import FeatureFlagService

        flag_service = FeatureFlagService(settings)
        enabled = await flag_service.is_enabled(flag_key)
        if not enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{flag_key}' is not available in {settings.deployment_mode.value} mode.",
            )
        return True

    return _check


# ── Role Checking ──────────────────────────────

def require_role(required_role: str):
    """
    Factory for role-based access control.
    Usage: Depends(require_role("admin"))
    """

    async def _check(user=Depends(get_current_user)):
        role_hierarchy = {"user": 0, "admin": 1, "superadmin": 2}
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' or higher is required.",
            )
        return user

    return _check
