/**
 * PIEE SDK — Type Definitions
 *
 * TypeScript types matching the OpenAI-compatible API schemas.
 * These types are shared between the SDK and consumer applications.
 */

// ── Configuration ─────────────────────────────

export interface PIEEConfig {
    /** API base URL. Defaults to https://api.piee.app */
    baseURL?: string;
    /** API key for authentication (Bearer token or API key) */
    apiKey?: string;
    /** Request timeout in milliseconds */
    timeout?: number;
    /** Default headers to include in all requests */
    defaultHeaders?: Record<string, string>;
}

// ── Chat Completions ──────────────────────────

export interface ChatMessage {
    role: "system" | "user" | "assistant" | "tool";
    content: string | null;
    name?: string;
    tool_calls?: ToolCall[];
    tool_call_id?: string;
}

export interface ToolCall {
    id: string;
    type: "function";
    function: {
        name: string;
        arguments: string;
    };
}

export interface ChatCompletionRequest {
    model: string;
    messages: ChatMessage[];
    temperature?: number;
    top_p?: number;
    n?: number;
    max_tokens?: number;
    stream?: boolean;
    stop?: string | string[];
    presence_penalty?: number;
    frequency_penalty?: number;
    user?: string;
}

export interface ChatCompletionChoice {
    index: number;
    message: ChatMessage;
    finish_reason: "stop" | "length" | "tool_calls" | "content_filter" | null;
}

export interface Usage {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
}

export interface ChatCompletionResponse {
    id: string;
    object: "chat.completion";
    created: number;
    model: string;
    choices: ChatCompletionChoice[];
    usage: Usage;
    system_fingerprint?: string;
}

// ── Streaming ─────────────────────────────────

export interface ChatCompletionChunkDelta {
    role?: string;
    content?: string;
}

export interface ChatCompletionChunkChoice {
    index: number;
    delta: ChatCompletionChunkDelta;
    finish_reason: string | null;
}

export interface ChatCompletionChunk {
    id: string;
    object: "chat.completion.chunk";
    created: number;
    model: string;
    choices: ChatCompletionChunkChoice[];
}

// ── Embeddings ────────────────────────────────

export interface EmbeddingRequest {
    model: string;
    input: string | string[];
    encoding_format?: "float" | "base64";
    user?: string;
}

export interface EmbeddingData {
    object: "embedding";
    index: number;
    embedding: number[];
}

export interface EmbeddingResponse {
    object: "list";
    model: string;
    data: EmbeddingData[];
    usage: Usage;
}

// ── Models ────────────────────────────────────

export interface Model {
    id: string;
    object: "model";
    created: number;
    owned_by: string;
}

export interface ModelListResponse {
    object: "list";
    data: Model[];
}

// ── Auth ──────────────────────────────────────

export interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
}

// ── Billing ───────────────────────────────────

export interface WalletBalance {
    balance: number;
    currency: string;
    unlimited: boolean;
}

// ── Errors ────────────────────────────────────

export interface PIEEError {
    error: {
        message: string;
        type: string;
        code?: string;
        param?: string;
    };
}

// ── Usage Stats ───────────────────────────────

export interface UsageStats {
    total_requests: number;
    total_tokens: number;
    total_cost: number;
    period: string;
}
