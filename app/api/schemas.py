"""
PIEE — OpenAI-Compatible API Schemas

Pydantic models that match the OpenAI API specification.
Used by all v1 endpoints to ensure compatibility.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# ── Chat Completions ───────────────────────────


class ChatMessageSchema(BaseModel):
    role: str = Field(..., description="system | user | assistant | tool")
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequestSchema(BaseModel):
    model: str = Field(..., description="Model identifier, e.g. 'openai/gpt-4o'")
    messages: List[ChatMessageSchema]
    temperature: Optional[float] = Field(1.0, ge=0, le=2)
    top_p: Optional[float] = Field(1.0, ge=0, le=1)
    n: Optional[int] = Field(1, ge=1)
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2)
    user: Optional[str] = None


class ChatChoiceSchema(BaseModel):
    index: int
    message: ChatMessageSchema
    finish_reason: Optional[str] = "stop"


class UsageSchema(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponseSchema(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoiceSchema]
    usage: UsageSchema = UsageSchema()
    system_fingerprint: Optional[str] = None


# ── Streaming ──────────────────────────────────


class DeltaSchema(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class StreamChoiceSchema(BaseModel):
    index: int
    delta: DeltaSchema
    finish_reason: Optional[str] = None


class ChatCompletionChunkSchema(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoiceSchema]


# ── Embeddings ─────────────────────────────────


class EmbeddingRequestSchema(BaseModel):
    model: str = Field(..., description="Model identifier for embeddings")
    input: Union[str, List[str]] = Field(..., description="Text(s) to embed")
    encoding_format: Optional[str] = "float"
    user: Optional[str] = None


class EmbeddingDataSchema(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]


class EmbeddingResponseSchema(BaseModel):
    object: str = "list"
    model: str
    data: List[EmbeddingDataSchema]
    usage: UsageSchema = UsageSchema()


# ── Models ─────────────────────────────────────


class ModelSchema(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: list = []
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelListResponseSchema(BaseModel):
    object: str = "list"
    data: List[ModelSchema]
