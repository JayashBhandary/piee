"""
PIEE — Feature Flag Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FeatureFlagResponse(BaseModel):
    key: str
    value: bool
    description: Optional[str]
    local_default: bool
    cloud_default: bool

    class Config:
        from_attributes = True


class FeatureFlagUpdate(BaseModel):
    value: bool


class FeatureFlagBulk(BaseModel):
    """Bulk response for all feature flags."""
    flags: dict[str, bool]
    deployment_mode: str
