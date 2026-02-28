/**
 * PIEE SDK — Main Entry Point
 *
 * Unified SDK for the PIEE AI Infrastructure Platform.
 * Works with both local (http://localhost:8000) and cloud (https://api.piee.app) backends.
 *
 * Usage:
 *   // Cloud (default)
 *   const piee = new PIEE({ apiKey: "pk-..." });
 *
 *   // Local
 *   const piee = new PIEE({ baseURL: "http://localhost:8000", apiKey: "pk-..." });
 *
 *   // Chat completion
 *   const result = await piee.chat.completions.create({
 *     model: "openai/gpt-4o",
 *     messages: [{ role: "user", content: "Hello!" }],
 *   });
 */

import type {
    PIEEConfig,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChunk,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelListResponse,
    TokenResponse,
    WalletBalance,
    UsageStats,
    PIEEError,
} from "./types";

export * from "./types";

// ── HTTP Client ───────────────────────────────

class HTTPClient {
    private baseURL: string;
    private headers: Record<string, string>;
    private timeout: number;

    constructor(config: PIEEConfig) {
        this.baseURL = (config.baseURL || "https://api.piee.app").replace(/\/$/, "");
        this.timeout = config.timeout || 120000;
        this.headers = {
            "Content-Type": "application/json",
            ...config.defaultHeaders,
        };

        if (config.apiKey) {
            // Support both Bearer and X-API-Key
            if (config.apiKey.startsWith("pk-")) {
                this.headers["X-API-Key"] = config.apiKey;
            } else {
                this.headers["Authorization"] = `Bearer ${config.apiKey}`;
            }
        }
    }

    async request<T>(method: string, path: string, body?: unknown): Promise<T> {
        const url = `${this.baseURL}${path}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                method,
                headers: this.headers,
                body: body ? JSON.stringify(body) : undefined,
                signal: controller.signal,
            });

            if (!response.ok) {
                const error: PIEEError = await response.json().catch(() => ({
                    error: { message: `HTTP ${response.status}: ${response.statusText}`, type: "api_error" },
                }));
                throw new PIEEAPIError(
                    error.error.message,
                    response.status,
                    error.error.type,
                    error.error.code
                );
            }

            return await response.json() as T;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    async *stream(path: string, body: unknown): AsyncIterable<ChatCompletionChunk> {
        const url = `${this.baseURL}${path}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: this.headers,
                body: JSON.stringify(body),
                signal: controller.signal,
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({
                    error: { message: `HTTP ${response.status}`, type: "api_error" },
                }));
                throw new PIEEAPIError(error.error.message, response.status, error.error.type);
            }

            const reader = response.body?.getReader();
            if (!reader) throw new Error("No response body");

            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed.startsWith("data: ")) continue;
                    const data = trimmed.slice(6);
                    if (data === "[DONE]") return;

                    try {
                        yield JSON.parse(data) as ChatCompletionChunk;
                    } catch {
                        // Skip malformed chunks
                    }
                }
            }
        } finally {
            clearTimeout(timeoutId);
        }
    }
}

// ── Error Class ───────────────────────────────

export class PIEEAPIError extends Error {
    status: number;
    type: string;
    code?: string;

    constructor(message: string, status: number, type: string, code?: string) {
        super(message);
        this.name = "PIEEAPIError";
        this.status = status;
        this.type = type;
        this.code = code;
    }
}

// ── Resource Namespaces ───────────────────────

class Completions {
    constructor(private client: HTTPClient) { }

    /**
     * Create a chat completion.
     *
     * @example
     * const result = await piee.chat.completions.create({
     *   model: "openai/gpt-4o",
     *   messages: [{ role: "user", content: "What is AI?" }],
     * });
     */
    async create(params: ChatCompletionRequest): Promise<ChatCompletionResponse> {
        return this.client.request<ChatCompletionResponse>("POST", "/v1/chat/completions", {
            ...params,
            stream: false,
        });
    }

    /**
     * Create a streaming chat completion.
     *
     * @example
     * for await (const chunk of piee.chat.completions.stream({
     *   model: "openai/gpt-4o",
     *   messages: [{ role: "user", content: "Tell me a story" }],
     * })) {
     *   process.stdout.write(chunk.choices[0]?.delta?.content || "");
     * }
     */
    stream(params: ChatCompletionRequest): AsyncIterable<ChatCompletionChunk> {
        return this.client.stream("/v1/chat/completions", { ...params, stream: true });
    }
}

class Chat {
    completions: Completions;

    constructor(client: HTTPClient) {
        this.completions = new Completions(client);
    }
}

class Embeddings {
    constructor(private client: HTTPClient) { }

    /**
     * Create embeddings.
     *
     * @example
     * const result = await piee.embeddings.create({
     *   model: "openai/text-embedding-3-small",
     *   input: "Hello world",
     * });
     */
    async create(params: EmbeddingRequest): Promise<EmbeddingResponse> {
        return this.client.request<EmbeddingResponse>("POST", "/v1/embeddings", params);
    }
}

class Models {
    constructor(private client: HTTPClient) { }

    /**
     * List all available models.
     *
     * @example
     * const models = await piee.models.list();
     */
    async list(): Promise<ModelListResponse> {
        return this.client.request<ModelListResponse>("GET", "/v1/models");
    }
}

class Auth {
    constructor(private client: HTTPClient) { }

    /** Login and receive an access token. */
    async login(email: string, password: string): Promise<TokenResponse> {
        return this.client.request<TokenResponse>("POST", "/auth/login", { email, password });
    }
}

class Billing {
    constructor(private client: HTTPClient) { }

    /** Get current credit balance. */
    async balance(): Promise<WalletBalance> {
        return this.client.request<WalletBalance>("GET", "/billing/balance");
    }
}

class Usage {
    constructor(private client: HTTPClient) { }

    /** Get usage statistics. */
    async stats(): Promise<UsageStats> {
        return this.client.request<UsageStats>("GET", "/audit/usage");
    }
}

// ── Main SDK Class ────────────────────────────

/**
 * PIEE SDK — Unified AI Infrastructure Client
 *
 * The SDK is completely backend-agnostic. It does not
 * know or care whether the backend is local or cloud.
 * Routing is handled entirely server-side.
 *
 * @example
 * // Cloud deployment (default)
 * const piee = new PIEE({ apiKey: "pk-your-api-key" });
 *
 * // Local deployment
 * const piee = new PIEE({
 *   baseURL: "http://localhost:8000",
 *   apiKey: "pk-your-local-key",
 * });
 *
 * // Use it (identical regardless of backend)
 * const response = await piee.chat.completions.create({
 *   model: "openai/gpt-4o",
 *   messages: [{ role: "user", content: "Hello!" }],
 * });
 */
export class PIEE {
    /** Chat completions namespace */
    chat: Chat;
    /** Embeddings namespace */
    embeddings: Embeddings;
    /** Models namespace */
    models: Models;
    /** Auth namespace */
    auth: Auth;
    /** Billing namespace */
    billing: Billing;
    /** Usage namespace */
    usage: Usage;

    private client: HTTPClient;

    constructor(config: PIEEConfig = {}) {
        this.client = new HTTPClient(config);
        this.chat = new Chat(this.client);
        this.embeddings = new Embeddings(this.client);
        this.models = new Models(this.client);
        this.auth = new Auth(this.client);
        this.billing = new Billing(this.client);
        this.usage = new Usage(this.client);
    }
}

export default PIEE;
