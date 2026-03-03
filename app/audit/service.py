"""
PIEE — Audit & Usage Logging Service

Writes UsageLog and AuditLog records.
Calculates cost based on model pricing from ModelRegistry.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.config import Settings

logger = logging.getLogger(__name__)


class AuditService:
    """Handles usage logging and audit trail recording."""

    @staticmethod
    async def log_usage(
        user_id: str,
        model_id: str,
        request_type: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        settings: Settings,
        status_code: int = 200,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log a model usage event.
        Calculates cost from ModelRegistry pricing data.
        """
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                # Look up model pricing
                model_record = await db.modelregistry.find_unique(
                    where={"modelId": model_id}
                )

                cost = 0.0
                model_registry_id = None

                if model_record:
                    model_registry_id = model_record.id
                    # Calculate cost: price per million tokens
                    cost = (input_tokens * model_record.inputPricePerM / 1_000_000) + (
                        output_tokens * model_record.outputPricePerM / 1_000_000
                    )

                if model_registry_id:
                    await db.usagelog.create(
                        data={
                            "userId": user_id,
                            "modelRegistryId": model_registry_id,
                            "requestType": request_type,
                            "inputTokens": input_tokens,
                            "outputTokens": output_tokens,
                            "totalTokens": input_tokens + output_tokens,
                            "latencyMs": latency_ms,
                            "cost": cost,
                            "statusCode": status_code,
                            "errorMessage": error_message,
                        }
                    )

                # Deduct credits if billing is enabled
                from app.flags.service import FeatureFlagService

                flag_service = FeatureFlagService(settings)
                if await flag_service.is_enabled("billing_enabled") and cost > 0:
                    from app.billing.service import BillingService

                    await BillingService.deduct_credits(
                        user_id=user_id, amount=cost, reference_id=model_id
                    )

            finally:
                await db.disconnect()
        except Exception as e:
            logger.warning(f"Failed to log usage: {e}")

    @staticmethod
    async def log_audit(
        action: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Record an audit trail event."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                await db.auditlog.create(
                    data={
                        "userId": user_id,
                        "action": action,
                        "resource": resource,
                        "details": json.dumps(details or {}),
                        "ipAddress": ip_address,
                        "userAgent": user_agent,
                    }
                )
            finally:
                await db.disconnect()
        except Exception as e:
            logger.warning(f"Failed to log audit: {e}")

    @staticmethod
    async def get_usage_stats(user_id: str, limit: int = 100):
        """Get usage statistics for a user."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                records = await db.usagelog.find_many(
                    where={"userId": user_id},
                    order={"createdAt": "desc"},
                    take=limit,
                )
                total_tokens = sum(r.totalTokens for r in records)
                total_cost = sum(r.cost for r in records)
                return {
                    "total_requests": len(records),
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "records": records,
                }
            finally:
                await db.disconnect()
        except Exception:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "records": [],
            }
