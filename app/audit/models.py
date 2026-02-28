"""
PIEE — Audit Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class UsageRecord(BaseModel):
    id: str
    user_id: str
    model_id: str
    request_type: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost: float
    status_code: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditEntry(BaseModel):
    id: str
    user_id: Optional[str]
    action: str
    resource: Optional[str]
    details: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost: float
    period: str  # "day" | "week" | "month"
    breakdown: List[UsageRecord] = []
