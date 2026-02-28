"""
PIEE — Router Pydantic Schemas

Data models for routing requests and model registry.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RoutingMode(str, Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    INTERNAL = "INTERNAL"


class RoutingRequest(BaseModel):
    """Incoming routing request."""
    model: str = Field(..., description="Model identifier (e.g., 'openai/gpt-4o')")
    request_type: str = Field(default="chat", description="chat | embedding | completion")
    preferred_mode: Optional[RoutingMode] = None
    user_id: Optional[str] = None


class RoutingDecision(BaseModel):
    """Result of a routing decision."""
    model_id: str
    provider_name: str
    routing_mode: RoutingMode
    resolved_model: str  # The actual model name to send to the provider
    fallback_chain: List[str] = []  # List of fallback model IDs


class ModelInfoResponse(BaseModel):
    """Model info for API responses (OpenAI-compatible)."""
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: list = []
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelRegistryEntry(BaseModel):
    """Full model registry entry for admin views."""
    id: str
    model_id: str
    display_name: str
    provider: str
    routing_mode: str
    capabilities: List[str]
    context_window: int
    input_price_per_m: float
    output_price_per_m: float
    is_active: bool
    is_premium: bool
    fallback_model_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelRegistryCreate(BaseModel):
    """Create a new model registry entry."""
    model_id: str
    display_name: str
    provider: str
    routing_mode: str = "REMOTE"
    capabilities: List[str] = ["chat"]
    context_window: int = 4096
    input_price_per_m: float = 0
    output_price_per_m: float = 0
    is_active: bool = True
    is_premium: bool = False
    fallback_model_id: Optional[str] = None


class ModelRegistryUpdate(BaseModel):
    """Update an existing model registry entry."""
    display_name: Optional[str] = None
    routing_mode: Optional[str] = None
    capabilities: Optional[List[str]] = None
    context_window: Optional[int] = None
    input_price_per_m: Optional[float] = None
    output_price_per_m: Optional[float] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    fallback_model_id: Optional[str] = None
