"""
PIEE — Auth Router

Endpoints for user registration, login, and API key management.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma

from app.auth.models import (
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.auth.service import AuthService
from app.config import Settings, get_settings
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Register ───────────────────────────────────


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    body: UserCreate,
    db: Prisma = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Register a new user account."""
    # Check if email already exists
    existing = await db.user.find_unique(where={"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    hashed = AuthService.hash_password(body.password)
    user = await db.user.create(
        data={
            "email": body.email,
            "password": hashed,
            "name": body.name,
            "role": "admin" if settings.is_local else "user",
        }
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.isActive,
        created_at=user.createdAt,
    )


# ── Login ──────────────────────────────────────


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLogin,
    db: Prisma = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Authenticate and receive a JWT access token."""
    user = await db.user.find_unique(where={"email": body.email})
    if not user or not AuthService.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    auth_service = AuthService(settings)
    token, expires_in = auth_service.create_jwt(user.id, user.email, user.role)
    return TokenResponse(access_token=token, expires_in=expires_in)


# ── Me ─────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    """Get the currently authenticated user."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.isActive,
        created_at=user.createdAt,
    )


# ── API Keys ──────────────────────────────────


@router.post(
    "/api-keys", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    body: ApiKeyCreate,
    user=Depends(get_current_user),
    db: Prisma = Depends(get_db),
):
    """Create a new API key. The full key is only shown once."""
    raw_key = AuthService.generate_api_key()
    key_hash = AuthService.hash_api_key(raw_key)
    key_prefix = AuthService.get_key_prefix(raw_key)

    expires_at = None
    if body.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

    record = await db.apikey.create(
        data={
            "userId": user.id,
            "name": body.name,
            "keyHash": key_hash,
            "keyPrefix": key_prefix,
            "permissions": json.dumps(body.permissions),
            "expiresAt": expires_at,
        }
    )

    return ApiKeyCreated(
        id=record.id,
        name=record.name,
        key=raw_key,
        key_prefix=key_prefix,
        permissions=record.permissions,
        expires_at=record.expiresAt,
        created_at=record.createdAt,
    )


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    user=Depends(get_current_user),
    db: Prisma = Depends(get_db),
):
    """List all API keys for the current user."""
    keys = await db.apikey.find_many(
        where={"userId": user.id},
        order={"createdAt": "desc"},
    )
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.keyPrefix,
            permissions=k.permissions,
            is_active=k.isActive,
            last_used_at=k.lastUsedAt,
            expires_at=k.expiresAt,
            created_at=k.createdAt,
        )
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    user=Depends(get_current_user),
    db: Prisma = Depends(get_db),
):
    """Revoke (delete) an API key."""
    key = await db.apikey.find_unique(where={"id": key_id})
    if not key or key.userId != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found.",
        )
    await db.apikey.delete(where={"id": key_id})
