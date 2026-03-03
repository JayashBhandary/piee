"""
PIEE — OpenAI-Compatible Chat Completions Endpoint

POST /v1/chat/completions

Accepts standard OpenAI request format, routes through the RouterEngine,
and returns standard OpenAI response format. Supports streaming via SSE.
"""

from __future__ import annotations

import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    ChatCompletionRequestSchema,
    ChatCompletionResponseSchema,
    ChatChoiceSchema,
    ChatMessageSchema,
    UsageSchema,
)
from app.config import Settings, get_settings
from app.dependencies import get_current_user, get_db
from app.providers.base import (
    ChatCompletionRequest,
    ChatMessage,
)
from app.router.engine import RouterEngine
from app.router.models import RoutingRequest
from app.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["Chat Completions"])


def _get_router_engine(settings: Settings) -> RouterEngine:
    """Build a RouterEngine instance."""
    registry = ProviderRegistry(settings)
    return RouterEngine(settings, registry)


@router.post("/chat/completions", response_model=ChatCompletionResponseSchema)
async def chat_completions(
    body: ChatCompletionRequestSchema,
    request: Request,
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    OpenAI-compatible chat completion endpoint.

    All requests are routed through the RouterEngine.
    No provider logic exists in this endpoint.
    """
    start_time = time.time()

    # Build provider request
    provider_request = ChatCompletionRequest(
        model=body.model,
        messages=[
            ChatMessage(
                role=m.role,
                content=m.content
                if isinstance(m.content, str)
                else json.dumps(m.content)
                if m.content
                else None,
                name=m.name,
                tool_calls=m.tool_calls,
                tool_call_id=m.tool_call_id,
            )
            for m in body.messages
        ],
        temperature=body.temperature,
        top_p=body.top_p,
        max_tokens=body.max_tokens,
        stream=body.stream or False,
        stop=body.stop
        if isinstance(body.stop, list)
        else [body.stop]
        if body.stop
        else None,
        presence_penalty=body.presence_penalty,
        frequency_penalty=body.frequency_penalty,
        user=body.user,
    )

    # Route the request
    engine = _get_router_engine(settings)
    await engine.provider_registry.initialize()

    routing_request = RoutingRequest(
        model=body.model,
        request_type="chat",
        user_id=user.id,
    )

    try:
        provider, decision = await engine.route(routing_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # Handle streaming
    if body.stream:
        return StreamingResponse(
            _stream_response(
                provider,
                provider_request,
                user.id,
                decision.resolved_model,
                settings,
                start_time,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming
    try:
        result = await provider.chat_completion(provider_request)
    except Exception as e:
        logger.error(f"Provider error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider error: {str(e)}",
        )

    latency_ms = int((time.time() - start_time) * 1000)

    # Log usage
    await _log_usage(
        user_id=user.id,
        model_id=body.model,
        request_type="chat",
        input_tokens=result.usage.prompt_tokens,
        output_tokens=result.usage.completion_tokens,
        latency_ms=latency_ms,
        settings=settings,
    )

    return ChatCompletionResponseSchema(
        id=result.id,
        created=result.created,
        model=result.model,
        choices=[
            ChatChoiceSchema(
                index=c.index,
                message=ChatMessageSchema(
                    role=c.message.role, content=c.message.content
                ),
                finish_reason=c.finish_reason,
            )
            for c in result.choices
        ],
        usage=UsageSchema(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            total_tokens=result.usage.total_tokens,
        ),
    )


async def _stream_response(
    provider, request, user_id, resolved_model, settings, start_time
):
    """Generate SSE stream from provider."""
    total_tokens = 0
    try:
        async for chunk in provider.chat_completion_stream(request):
            data = chunk.model_dump()
            yield f"data: {json.dumps(data)}\n\n"
            total_tokens += 1
    except Exception as e:
        error_data = {"error": {"message": str(e), "type": "provider_error"}}
        yield f"data: {json.dumps(error_data)}\n\n"
    finally:
        yield "data: [DONE]\n\n"

    # Log streaming usage
    latency_ms = int((time.time() - start_time) * 1000)
    await _log_usage(
        user_id=user_id,
        model_id=request.model,
        request_type="chat",
        input_tokens=0,  # Token count not available in streaming
        output_tokens=total_tokens,
        latency_ms=latency_ms,
        settings=settings,
    )


async def _log_usage(
    user_id: str,
    model_id: str,
    request_type: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    settings: Settings,
):
    """Log usage asynchronously (best effort)."""
    try:
        from app.audit.service import AuditService

        await AuditService.log_usage(
            user_id=user_id,
            model_id=model_id,
            request_type=request_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            settings=settings,
        )
    except Exception as e:
        logger.warning(f"Failed to log usage: {e}")
