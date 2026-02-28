"""
PIEE — Audit Router

Endpoints for viewing usage stats and audit logs.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from app.audit.models import AuditEntry, UsageRecord, UsageStats
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/audit", tags=["Audit & Usage"])


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(
    limit: int = Query(default=100, le=1000),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Get usage statistics for the current user."""
    records = await db.usagelog.find_many(
        where={"userId": user.id},
        order={"createdAt": "desc"},
        take=limit,
    )

    total_tokens = sum(r.totalTokens for r in records)
    total_cost = sum(r.cost for r in records)

    return UsageStats(
        total_requests=len(records),
        total_tokens=total_tokens,
        total_cost=total_cost,
        period="all",
        breakdown=[
            UsageRecord(
                id=r.id,
                user_id=r.userId,
                model_id=r.modelRegistryId,
                request_type=r.requestType,
                input_tokens=r.inputTokens,
                output_tokens=r.outputTokens,
                total_tokens=r.totalTokens,
                latency_ms=r.latencyMs,
                cost=r.cost,
                status_code=r.statusCode,
                error_message=r.errorMessage,
                created_at=r.createdAt,
            )
            for r in records
        ],
    )


@router.get("/logs", response_model=List[AuditEntry])
async def get_audit_logs(
    limit: int = Query(default=50, le=500),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Get audit logs for the current user."""
    records = await db.auditlog.find_many(
        where={"userId": user.id},
        order={"createdAt": "desc"},
        take=limit,
    )

    return [
        AuditEntry(
            id=r.id,
            user_id=r.userId,
            action=r.action,
            resource=r.resource,
            details=r.details,
            ip_address=r.ipAddress,
            user_agent=r.userAgent,
            created_at=r.createdAt,
        )
        for r in records
    ]
