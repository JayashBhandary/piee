"""
PIEE — OpenAI-Compatible Embeddings Endpoint

POST /v1/embeddings
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import (
    EmbeddingRequestSchema,
    EmbeddingResponseSchema,
    EmbeddingDataSchema,
    UsageSchema,
)
from app.config import Settings, get_settings
from app.dependencies import get_current_user
from app.providers.base import EmbeddingRequest
from app.router.engine import RouterEngine
from app.router.models import RoutingRequest
from app.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["Embeddings"])


@router.post("/embeddings", response_model=EmbeddingResponseSchema)
async def create_embedding(
    body: EmbeddingRequestSchema,
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    OpenAI-compatible embeddings endpoint.
    Routes through the RouterEngine — no provider logic here.
    """
    start_time = time.time()

    # Build RouterEngine
    registry = ProviderRegistry(settings)
    engine = RouterEngine(settings, registry)
    await registry.initialize()

    # Route
    routing_request = RoutingRequest(
        model=body.model,
        request_type="embedding",
        user_id=user.id,
    )

    try:
        provider, decision = await engine.route(routing_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if not provider.supports_embeddings():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{decision.provider_name}' does not support embeddings.",
        )

    # Execute
    provider_request = EmbeddingRequest(
        model=body.model,
        input=body.input,
        encoding_format=body.encoding_format,
    )

    try:
        result = await provider.embedding(provider_request)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Embedding provider error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider error: {str(e)}",
        )

    latency_ms = int((time.time() - start_time) * 1000)

    # Log usage
    try:
        from app.audit.service import AuditService

        await AuditService.log_usage(
            user_id=user.id,
            model_id=body.model,
            request_type="embedding",
            input_tokens=result.usage.prompt_tokens,
            output_tokens=0,
            latency_ms=latency_ms,
            settings=settings,
        )
    except Exception:
        pass

    return EmbeddingResponseSchema(
        model=result.model,
        data=[
            EmbeddingDataSchema(index=d.index, embedding=d.embedding)
            for d in result.data
        ],
        usage=UsageSchema(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            total_tokens=result.usage.total_tokens,
        ),
    )
