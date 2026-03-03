"""
PIEE — BaseProvider Interface

Abstract base class that all provider adapters must implement.
This ensures decoupling between the router engine and individual providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from pydantic import BaseModel


# ── Shared Types ───────────────────────────────


class ProviderModelInfo(BaseModel):
    """Minimal model info returned by a provider."""

    id: str
    name: str
    provider: str
    capabilities: List[str] = []
    context_window: int = 4096


class ChatMessage(BaseModel):
    role: str  # system | user | assistant | tool
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: UsageInfo = UsageInfo()


class StreamDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class StreamChoice(BaseModel):
    index: int
    delta: StreamDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]


class EmbeddingRequest(BaseModel):
    model: str
    input: str | List[str]
    encoding_format: Optional[str] = "float"


class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    object: str = "list"
    model: str
    data: List[EmbeddingData]
    usage: UsageInfo = UsageInfo()


# ── Abstract Base Provider ─────────────────────


class BaseProvider(ABC):
    """
    Interface contract for all provider adapters.

    Every provider (OpenAI, Anthropic, local/Ollama, etc.)
    must implement these methods. The RouterEngine calls
    providers exclusively through this interface.
    """

    provider_name: str = "base"

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs
    ):
        self.api_key = api_key
        self.base_url = base_url
        self._config = kwargs

    @abstractmethod
    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Execute a non-streaming chat completion."""
        ...

    @abstractmethod
    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Execute a streaming chat completion, yielding chunks."""
        ...

    @abstractmethod
    async def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for the given input."""
        ...

    @abstractmethod
    async def list_models(self) -> List[ProviderModelInfo]:
        """List all models available from this provider."""
        ...

    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses."""
        return True

    def supports_embeddings(self) -> bool:
        """Whether this provider supports embedding generation."""
        return True

    async def health_check(self) -> bool:
        """Verify connectivity to the provider. Returns True if healthy."""
        try:
            await self.list_models()
            return True
        except Exception:
            return False
