"""
PIEE — Router Engine

The core routing brain of PIEE. Resolves model identifiers to providers
using config-driven logic from the ModelRegistry.

Architecture:
  API Endpoint → RouterEngine.route() → BaseProvider.chat_completion()

The engine NEVER hardcodes provider logic. All routing decisions
are driven by the ModelRegistry and ProviderConfig tables.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.config import Settings
from app.providers.base import BaseProvider
from app.providers.registry import ProviderRegistry
from app.router.models import RoutingDecision, RoutingMode, RoutingRequest

logger = logging.getLogger(__name__)


class RouterEngine:
    """
    Config-driven model router.

    Resolves a model identifier (e.g., "openai/gpt-4o") to a concrete
    BaseProvider instance and a routing decision.

    Supports:
      - Direct provider/model resolution
      - Fallback chains (model A → model B → model C)
      - Routing modes (LOCAL, REMOTE, INTERNAL)
      - Premium model gating via feature flags
    """

    def __init__(self, settings: Settings, provider_registry: ProviderRegistry):
        self.settings = settings
        self.provider_registry = provider_registry

    async def route(
        self, request: RoutingRequest
    ) -> tuple[BaseProvider, RoutingDecision]:
        """
        Resolve a routing request to a provider + decision.

        Returns:
            (provider_instance, routing_decision)

        Raises:
            ValueError: If no suitable provider is found
        """
        # 1. Try to resolve from ModelRegistry DB
        decision = await self._resolve_from_registry(request)

        if decision:
            provider = self.provider_registry.get(decision.provider_name)
            if provider:
                return provider, decision

        # 2. Try direct provider/model parsing (e.g., "openai/gpt-4o")
        decision = self._resolve_from_model_id(request)
        if decision:
            provider = self.provider_registry.get(decision.provider_name)
            if provider:
                return provider, decision

        # 3. Try fallback resolution
        fallback_result = await self._resolve_fallback(request)
        if fallback_result:
            return fallback_result

        raise ValueError(
            f"No provider found for model '{request.model}'. "
            f"Available providers: {self.provider_registry.list_providers()}"
        )

    async def _resolve_from_registry(
        self, request: RoutingRequest
    ) -> Optional[RoutingDecision]:
        """Look up the model in ModelRegistry DB."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                record = await db.modelregistry.find_unique(
                    where={"modelId": request.model}
                )
                if not record or not record.isActive:
                    return None

                # Check premium gating
                if record.isPremium:
                    from app.flags.service import FeatureFlagService

                    flag_service = FeatureFlagService(self.settings)
                    if not await flag_service.is_enabled("premium_models_enabled"):
                        logger.warning(
                            f"Premium model '{request.model}' blocked by feature flag"
                        )
                        return None

                # Determine routing mode
                routing_mode = RoutingMode(record.routingMode)
                if request.preferred_mode:
                    routing_mode = request.preferred_mode

                # Build fallback chain
                fallback_chain = []
                if record.fallbackModelId:
                    fallback_chain = await self._build_fallback_chain(
                        record.fallbackModelId, db
                    )

                return RoutingDecision(
                    model_id=record.modelId,
                    provider_name=record.provider,
                    routing_mode=routing_mode,
                    resolved_model=record.modelId.split("/")[-1],
                    fallback_chain=fallback_chain,
                )
            finally:
                await db.disconnect()
        except Exception as e:
            logger.debug(f"Registry lookup failed: {e}")
            return None

    def _resolve_from_model_id(
        self, request: RoutingRequest
    ) -> Optional[RoutingDecision]:
        """Parse provider from model ID format: 'provider/model-name'."""
        if "/" not in request.model:
            # Try all available providers
            for provider_name in self.provider_registry.list_providers():
                if self.provider_registry.is_available(provider_name):
                    return RoutingDecision(
                        model_id=request.model,
                        provider_name=provider_name,
                        routing_mode=RoutingMode.REMOTE,
                        resolved_model=request.model,
                    )
            return None

        parts = request.model.split("/", 1)
        provider_name = parts[0]
        model_name = parts[1]

        if not self.provider_registry.is_available(provider_name):
            return None

        routing_mode = (
            RoutingMode.LOCAL if provider_name == "local" else RoutingMode.REMOTE
        )
        if request.preferred_mode:
            routing_mode = request.preferred_mode

        return RoutingDecision(
            model_id=request.model,
            provider_name=provider_name,
            routing_mode=routing_mode,
            resolved_model=model_name,
        )

    async def _resolve_fallback(
        self, request: RoutingRequest
    ) -> Optional[tuple[BaseProvider, RoutingDecision]]:
        """Try fallback providers if the primary one is unavailable."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                # Find models with matching base name
                base_name = request.model.split("/")[-1]
                models = await db.modelregistry.find_many(
                    where={
                        "isActive": True,
                        "modelId": {"contains": base_name},
                    }
                )

                for model in models:
                    provider = self.provider_registry.get(model.provider)
                    if provider:
                        return provider, RoutingDecision(
                            model_id=model.modelId,
                            provider_name=model.provider,
                            routing_mode=RoutingMode(model.routingMode),
                            resolved_model=model.modelId.split("/")[-1],
                        )
            finally:
                await db.disconnect()
        except Exception:
            pass

        return None

    async def _build_fallback_chain(self, start_model_id: str, db) -> list[str]:
        """Build a chain of fallback models."""
        chain = []
        current_id = start_model_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            chain.append(current_id)
            record = await db.modelregistry.find_unique(where={"modelId": current_id})
            if record and record.fallbackModelId:
                current_id = record.fallbackModelId
            else:
                break

        return chain

    async def execute_with_fallback(self, request: RoutingRequest, execute_fn):
        """
        Execute a request with automatic fallback on failure.

        execute_fn: async callable that takes (provider, resolved_model) and returns result
        """
        provider, decision = await self.route(request)

        try:
            return await execute_fn(provider, decision.resolved_model)
        except Exception as primary_error:
            logger.warning(
                f"Primary provider '{decision.provider_name}' failed: {primary_error}. "
                f"Trying {len(decision.fallback_chain)} fallbacks..."
            )

            for fallback_model_id in decision.fallback_chain:
                try:
                    fallback_request = RoutingRequest(
                        model=fallback_model_id,
                        request_type=request.request_type,
                        user_id=request.user_id,
                    )
                    fb_provider, fb_decision = await self.route(fallback_request)
                    return await execute_fn(fb_provider, fb_decision.resolved_model)
                except Exception as fb_error:
                    logger.warning(
                        f"Fallback '{fallback_model_id}' also failed: {fb_error}"
                    )
                    continue

            raise primary_error  # All fallbacks exhausted
