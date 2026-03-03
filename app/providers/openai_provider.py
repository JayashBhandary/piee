"""
PIEE — OpenAI Provider Adapter

Implements BaseProvider for the OpenAI API.
Uses httpx for async HTTP calls.
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


class OpenAIProvider(BaseProvider):
    """OpenAI API adapter."""

    provider_name = "openai"

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs
    ):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _build_payload(self, request: ChatCompletionRequest) -> dict:
        payload = {
            "model": request.model.split("/")[-1],  # Strip provider prefix
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": request.stream,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.stop:
            payload["stop"] = request.stop
        if request.presence_penalty:
            payload["presence_penalty"] = request.presence_penalty
        if request.frequency_penalty:
            payload["frequency_penalty"] = request.frequency_penalty
        return payload

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        client = self._get_client()
        payload = self._build_payload(request)
        payload["stream"] = False

        resp = await client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
            created=data.get("created", int(time.time())),
            model=data.get("model", request.model),
            choices=[
                ChatCompletionChoice(
                    index=c["index"],
                    message=ChatMessage(**c["message"]),
                    finish_reason=c.get("finish_reason", "stop"),
                )
                for c in data.get("choices", [])
            ],
            usage=UsageInfo(**data.get("usage", {})),
        )

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        client = self._get_client()
        payload = self._build_payload(request)
        payload["stream"] = True

        async with client.stream("POST", "/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    yield ChatCompletionChunk(
                        id=data.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
                        created=data.get("created", int(time.time())),
                        model=data.get("model", request.model),
                        choices=[
                            StreamChoice(
                                index=c["index"],
                                delta=StreamDelta(**c.get("delta", {})),
                                finish_reason=c.get("finish_reason"),
                            )
                            for c in data.get("choices", [])
                        ],
                    )
                except json.JSONDecodeError:
                    continue

    async def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        client = self._get_client()
        payload = {
            "model": request.model.split("/")[-1],
            "input": request.input,
        }
        if request.encoding_format:
            payload["encoding_format"] = request.encoding_format

        resp = await client.post("/embeddings", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return EmbeddingResponse(
            model=data.get("model", request.model),
            data=[
                EmbeddingData(index=d["index"], embedding=d["embedding"])
                for d in data.get("data", [])
            ],
            usage=UsageInfo(**data.get("usage", {})),
        )

    async def list_models(self) -> List[ProviderModelInfo]:
        client = self._get_client()
        resp = await client.get("/models")
        resp.raise_for_status()
        data = resp.json()

        return [
            ProviderModelInfo(
                id=f"openai/{m['id']}",
                name=m["id"],
                provider="openai",
                capabilities=["chat"],
            )
            for m in data.get("data", [])
        ]
