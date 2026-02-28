/**
 * PIEE Dashboard — API Client
 *
 * Wraps fetch calls to the PIEE backend.
 * Reads NEXT_PUBLIC_API_URL to connect to either local or cloud.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIClient {
    private baseURL: string;
    private token: string | null = null;

    constructor() {
        this.baseURL = API_URL;
        if (typeof window !== "undefined") {
            this.token = localStorage.getItem("piee_token");
        }
    }

    setToken(token: string) {
        this.token = token;
        if (typeof window !== "undefined") {
            localStorage.setItem("piee_token", token);
        }
    }

    clearToken() {
        this.token = null;
        if (typeof window !== "undefined") {
            localStorage.removeItem("piee_token");
        }
    }

    private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
        const headers: Record<string, string> = {
            "Content-Type": "application/json",
        };
        if (this.token) {
            headers["Authorization"] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${path}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Request failed" }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Auth
    async login(email: string, password: string) {
        const result = await this.request<{ access_token: string; expires_in: number }>(
            "POST",
            "/auth/login",
            { email, password }
        );
        this.setToken(result.access_token);
        return result;
    }

    async register(email: string, password: string, name?: string) {
        return this.request("POST", "/auth/register", { email, password, name });
    }

    async getMe() {
        return this.request("GET", "/auth/me");
    }

    // Models
    async listModels() {
        return this.request("GET", "/v1/models");
    }

    // API Keys
    async listApiKeys() {
        return this.request("GET", "/auth/api-keys");
    }

    async createApiKey(name: string) {
        return this.request("POST", "/auth/api-keys", { name });
    }

    async deleteApiKey(id: string) {
        return this.request("DELETE", `/auth/api-keys/${id}`);
    }

    // Usage
    async getUsageStats() {
        return this.request("GET", "/audit/usage");
    }

    // Billing
    async getBalance() {
        return this.request("GET", "/billing/balance");
    }

    // Health
    async getHealth() {
        return this.request("GET", "/health");
    }
}

export const api = new APIClient();
export default api;
