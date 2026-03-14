"""
PIEE — Ollama Provider Adapter (Ollama Inference)

Implements BaseProvider for local inference servers.
Compatible with Ollama's OpenAI-compatible API.
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


class OllamaProvider(BaseProvider):
    """Ollama local inference server adapter."""

    provider_name = "ollama"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self.base_url = base_url or "http://localhost:11434"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=httpx.Timeout(300.0, connect=10.0),  # long timeout for local
            )
        return self._client

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        client = self._get_client()

        # Ollama's OpenAI-compatible endpoint
        payload = {
            "model": request.model.split("/")[-1],
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
            "stream": False,
        }
        if request.temperature is not None:
            payload["options"] = {"temperature": request.temperature}
        if request.max_tokens is not None:
            payload.setdefault("options", {})["num_predict"] = request.max_tokens

        try:
            # Try OpenAI-compatible endpoint first
            resp = await client.post("/v1/chat/completions", json=payload)
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
        except httpx.HTTPStatusError:
            # Fallback to Ollama native endpoint
            native_payload = {
                "model": request.model.split("/")[-1],
                "messages": [m.model_dump(exclude_none=True) for m in request.messages],
                "stream": False,
            }
            resp = await client.post("/api/chat", json=native_payload)
            resp.raise_for_status()
            data = resp.json()

            return ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
                created=int(time.time()),
                model=data.get("model", request.model),
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=data.get("message", {}).get("content", ""),
                        ),
                        finish_reason="stop" if data.get("done") else None,
                    )
                ],
                usage=UsageInfo(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0)
                    + data.get("eval_count", 0),
                ),
            )

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        client = self._get_client()
        payload = {
            "model": request.model.split("/")[-1],
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
            "stream": True,
        }

        async with client.stream("POST", "/v1/chat/completions", json=payload) as resp:
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

        try:
            resp = await client.post("/v1/embeddings", json=payload)
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
        except httpx.HTTPStatusError:
            # Fallback to Ollama native embedding endpoint
            input_text = (
                request.input if isinstance(request.input, str) else request.input[0]
            )
            resp = await client.post(
                "/api/embeddings",
                json={
                    "model": request.model.split("/")[-1],
                    "prompt": input_text,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            return EmbeddingResponse(
                model=request.model,
                data=[EmbeddingData(index=0, embedding=data.get("embedding", []))],
                usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            )

    async def list_models(self) -> List[ProviderModelInfo]:
        client = self._get_client()
        try:
            resp = await client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()

            return [
                ProviderModelInfo(
                    id=f"ollama/{m['name']}",
                    name=m["name"],
                    provider="ollama",
                    capabilities=["chat"],
                )
                for m in data.get("models", [])
            ]
        except Exception:
            return []

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            resp = await client.get("/")
            return resp.status_code == 200
        except Exception:
            return False
