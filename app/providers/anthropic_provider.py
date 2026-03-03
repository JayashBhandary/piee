"""
PIEE — Anthropic Provider Adapter

Implements BaseProvider for the Anthropic Messages API.
Translates OpenAI-format requests to Anthropic's format and back.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import AsyncIterator, List, Optional

import httpx

from app.providers.base import (
    BaseProvider,
    ChatCompletionChunk,
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    EmbeddingData,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderModelInfo,
    StreamChoice,
    StreamDelta,
    UsageInfo,
)


class AnthropicProvider(BaseProvider):
    """Anthropic Messages API adapter."""

    provider_name = "anthropic"

    # Anthropic models and capabilities
    KNOWN_MODELS = [
        {
            "id": "claude-3-5-sonnet-20241022",
            "name": "Claude 3.5 Sonnet",
            "ctx": 200000,
        },
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "ctx": 200000},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "ctx": 200000},
    ]

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs
    ):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self.base_url = base_url or "https://api.anthropic.com"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "x-api-key": self.api_key or "",
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _translate_messages(
        self, messages: List[ChatMessage]
    ) -> tuple[Optional[str], List[dict]]:
        """Separate system prompt from messages (Anthropic treats system separately)."""
        system_prompt = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                anthropic_messages.append(
                    {
                        "role": msg.role
                        if msg.role in ("user", "assistant")
                        else "user",
                        "content": msg.content or "",
                    }
                )

        return system_prompt, anthropic_messages

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        client = self._get_client()
        system_prompt, messages = self._translate_messages(request.messages)

        payload: dict = {
            "model": request.model.split("/")[-1],
            "messages": messages,
            "max_tokens": request.max_tokens or 4096,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop:
            payload["stop_sequences"] = request.stop

        resp = await client.post("/v1/messages", json=payload)
        resp.raise_for_status()
        data = resp.json()

        # Translate Anthropic response → OpenAI format
        content_blocks = data.get("content", [])
        text_content = " ".join(
            block.get("text", "")
            for block in content_blocks
            if block.get("type") == "text"
        )

        usage = data.get("usage", {})

        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
            created=int(time.time()),
            model=data.get("model", request.model),
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=text_content),
                    finish_reason=self._map_stop_reason(
                        data.get("stop_reason", "end_turn")
                    ),
                )
            ],
            usage=UsageInfo(
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0)
                + usage.get("output_tokens", 0),
            ),
        )

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        client = self._get_client()
        system_prompt, messages = self._translate_messages(request.messages)

        payload: dict = {
            "model": request.model.split("/")[-1],
            "messages": messages,
            "max_tokens": request.max_tokens or 4096,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        async with client.stream("POST", "/v1/messages", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if not data_str:
                    continue
                try:
                    event = json.loads(data_str)
                    event_type = event.get("type", "")

                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield ChatCompletionChunk(
                                id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
                                created=int(time.time()),
                                model=request.model,
                                choices=[
                                    StreamChoice(
                                        index=0,
                                        delta=StreamDelta(
                                            content=delta.get("text", "")
                                        ),
                                        finish_reason=None,
                                    )
                                ],
                            )
                    elif event_type == "message_stop":
                        yield ChatCompletionChunk(
                            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
                            created=int(time.time()),
                            model=request.model,
                            choices=[
                                StreamChoice(
                                    index=0,
                                    delta=StreamDelta(),
                                    finish_reason="stop",
                                )
                            ],
                        )
                        break
                except json.JSONDecodeError:
                    continue

    async def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Anthropic does not natively support embeddings."""
        raise NotImplementedError(
            "Anthropic does not offer an embeddings API. "
            "Use OpenAI or a local model for embeddings."
        )

    def supports_embeddings(self) -> bool:
        return False

    async def list_models(self) -> List[ProviderModelInfo]:
        return [
            ProviderModelInfo(
                id=f"anthropic/{m['id']}",
                name=m["name"],
                provider="anthropic",
                capabilities=["chat", "vision"],
                context_window=m["ctx"],
            )
            for m in self.KNOWN_MODELS
        ]

    @staticmethod
    def _map_stop_reason(reason: str) -> str:
        mapping = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
        }
        return mapping.get(reason, "stop")
