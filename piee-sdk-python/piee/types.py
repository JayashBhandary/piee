from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

# ── Configuration ─────────────────────────────

class PIEEConfig(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: Optional[float] = 120.0
    default_headers: Optional[Dict[str, str]] = None

# ── Chat Completions ──────────────────────────

class ToolCallFunction(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: ToolCallFunction

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str]
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter"]] = None

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage
    system_fingerprint: Optional[str] = None

# ── Streaming ─────────────────────────────────

class ChatCompletionChunkDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None

class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]

# ── Embeddings ────────────────────────────────

class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    encoding_format: Optional[Literal["float", "base64"]] = "float"
    user: Optional[str] = None

class EmbeddingData(BaseModel):
    object: Literal["embedding"] = "embedding"
    index: int
    embedding: List[float]

class EmbeddingResponse(BaseModel):
    object: Literal["list"] = "list"
    model: str
    data: List[EmbeddingData]
    usage: Usage

# ── Models ────────────────────────────────────

class Model(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int
    owned_by: str

class ModelListResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[Model]

# ── Auth ──────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# ── Billing ───────────────────────────────────

class WalletBalance(BaseModel):
    balance: float
    currency: str
    unlimited: bool

# ── Usage Stats ───────────────────────────────

class UsageStats(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost: float
    period: str
