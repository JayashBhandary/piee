"""
PIEE — Model Registry Service

CRUD operations for model registry and provider configurations.
All model data is stored in the ModelRegistry table — no hardcoded models.
"""

from __future__ import annotations

import json
import time
from typing import List, Optional

from prisma import Prisma

from app.router.models import (
    ModelInfoResponse,
    ModelRegistryCreate,
    ModelRegistryEntry,
    ModelRegistryUpdate,
)


class ModelRegistryService:
    """Manages the ModelRegistry table — the single source of truth for all models."""

    # ── Seed Data ──────────────────────────────

    DEFAULT_MODELS = [
        {
            "modelId": "openai/gpt-4o",
            "displayName": "GPT-4o",
            "provider": "openai",
            "routingMode": "REMOTE",
            "capabilities": json.dumps(["chat", "vision"]),
            "contextWindow": 128000,
            "inputPricePerM": 2.50,
            "outputPricePerM": 10.00,
            "isPremium": False,
        },
        {
            "modelId": "openai/gpt-4o-mini",
            "displayName": "GPT-4o Mini",
            "provider": "openai",
            "routingMode": "REMOTE",
            "capabilities": json.dumps(["chat", "vision"]),
            "contextWindow": 128000,
            "inputPricePerM": 0.15,
            "outputPricePerM": 0.60,
            "isPremium": False,
        },
        {
            "modelId": "openai/text-embedding-3-small",
            "displayName": "Text Embedding 3 Small",
            "provider": "openai",
            "routingMode": "REMOTE",
            "capabilities": json.dumps(["embeddings"]),
            "contextWindow": 8191,
            "inputPricePerM": 0.02,
            "outputPricePerM": 0,
            "isPremium": False,
        },
        {
            "modelId": "anthropic/claude-3-5-sonnet-20241022",
            "displayName": "Claude 3.5 Sonnet",
            "provider": "anthropic",
            "routingMode": "REMOTE",
            "capabilities": json.dumps(["chat", "vision"]),
            "contextWindow": 200000,
            "inputPricePerM": 3.00,
            "outputPricePerM": 15.00,
            "isPremium": False,
        },
        {
            "modelId": "anthropic/claude-3-5-haiku-20241022",
            "displayName": "Claude 3.5 Haiku",
            "provider": "anthropic",
            "routingMode": "REMOTE",
            "capabilities": json.dumps(["chat"]),
            "contextWindow": 200000,
            "inputPricePerM": 0.80,
            "outputPricePerM": 4.00,
            "isPremium": False,
        },
    ]

    @staticmethod
    async def seed_defaults(db: Prisma) -> int:
        """Seed default models if the registry is empty. Returns count seeded."""
        existing = await db.modelregistry.count()
        if existing > 0:
            return 0

        count = 0
        for model_data in ModelRegistryService.DEFAULT_MODELS:
            try:
                await db.modelregistry.create(data=model_data)
                count += 1
            except Exception:
                pass  # Skip duplicates
        return count

    # ── CRUD ───────────────────────────────────

    @staticmethod
    async def list_models(
        db: Prisma,
        active_only: bool = True,
        provider: Optional[str] = None,
    ) -> list:
        """List models from registry."""
        where: dict = {}
        if active_only:
            where["isActive"] = True
        if provider:
            where["provider"] = provider

        return await db.modelregistry.find_many(
            where=where,
            order={"modelId": "asc"},
        )

    @staticmethod
    async def get_model(db: Prisma, model_id: str):
        """Get a single model by its model ID."""
        return await db.modelregistry.find_unique(where={"modelId": model_id})

    @staticmethod
    async def create_model(db: Prisma, data: ModelRegistryCreate):
        """Create a new model registry entry."""
        return await db.modelregistry.create(
            data={
                "modelId": data.model_id,
                "displayName": data.display_name,
                "provider": data.provider,
                "routingMode": data.routing_mode,
                "capabilities": json.dumps(data.capabilities),
                "contextWindow": data.context_window,
                "inputPricePerM": data.input_price_per_m,
                "outputPricePerM": data.output_price_per_m,
                "isActive": data.is_active,
                "isPremium": data.is_premium,
                "fallbackModelId": data.fallback_model_id,
            }
        )

    @staticmethod
    async def update_model(db: Prisma, model_id: str, data: ModelRegistryUpdate):
        """Update an existing model registry entry."""
        update_data: dict = {}
        if data.display_name is not None:
            update_data["displayName"] = data.display_name
        if data.routing_mode is not None:
            update_data["routingMode"] = data.routing_mode
        if data.capabilities is not None:
            update_data["capabilities"] = json.dumps(data.capabilities)
        if data.context_window is not None:
            update_data["contextWindow"] = data.context_window
        if data.input_price_per_m is not None:
            update_data["inputPricePerM"] = data.input_price_per_m
        if data.output_price_per_m is not None:
            update_data["outputPricePerM"] = data.output_price_per_m
        if data.is_active is not None:
            update_data["isActive"] = data.is_active
        if data.is_premium is not None:
            update_data["isPremium"] = data.is_premium
        if data.fallback_model_id is not None:
            update_data["fallbackModelId"] = data.fallback_model_id

        return await db.modelregistry.update(
            where={"modelId": model_id},
            data=update_data,
        )

    @staticmethod
    async def delete_model(db: Prisma, model_id: str):
        """Delete a model from the registry."""
        return await db.modelregistry.delete(where={"modelId": model_id})

    @staticmethod
    def to_openai_format(records: list) -> List[ModelInfoResponse]:
        """Convert registry records to OpenAI-compatible model list."""
        return [
            ModelInfoResponse(
                id=r.modelId,
                created=int(r.createdAt.timestamp())
                if r.createdAt
                else int(time.time()),
                owned_by=r.provider,
            )
            for r in records
        ]
