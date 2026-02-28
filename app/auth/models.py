"""
PIEE — Auth Pydantic Schemas

Request/response models for authentication endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# ── Requests ───────────────────────────────────

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: Optional[str] = Field(None, description="Display name")


class UserLogin(BaseModel):
    email: str
    password: str


class ApiKeyCreate(BaseModel):
    name: str = Field(..., description="Friendly name for the API key")
    permissions: List[str] = Field(default=["all"], description="Allowed permission scopes")
    expires_in_days: Optional[int] = Field(None, description="Expiry in days from now")


# ── Responses ──────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    permissions: str
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreated(BaseModel):
    """Returned only on creation — includes the full key (shown once)."""
    id: str
    name: str
    key: str  # Full API key — ONLY shown at creation time
    key_prefix: str
    permissions: str
    expires_at: Optional[datetime]
    created_at: datetime
