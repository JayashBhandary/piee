<p align="center">
  <img src="dashboard/assets/logo_ts.png" width="80" alt="PIEE Logo" />
</p>

<h1 align="center">PIEE</h1>
<p align="center"><strong>Hybrid AI Infrastructure Platform</strong></p>
<p align="center">OpenAI-compatible API gateway with local and cloud deployment support</p>

---

## Overview

PIEE is a unified AI infrastructure platform designed for dual deployment — run it **locally** as an open-source tool or deploy it as a **cloud SaaS**. A single codebase powers both modes.

### Key Features

- **OpenAI-compatible API** — Drop-in replacement endpoints (`/v1/chat/completions`, `/v1/embeddings`, `/v1/models`)
- **Multi-provider routing** — OpenAI, Anthropic, and local (Ollama) providers behind a unified interface
- **Config-driven router** — Model registry + fallback chains, no hardcoded provider logic
- **Ollama management** — Pull, sync, and manage local Ollama models directly from the dashboard
- **Sandbox playground** — Full-page interactive chat UI with streaming, markdown rendering, and configurable parameters (temperature, max tokens, system prompt)
- **Unified SDK** — TypeScript SDK that works identically across local and cloud
- **Feature flags** — Premium features gated by deployment mode
- **Credit wallet** — Usage-based billing (cloud only, unlimited in local)
- **Dashboard** — Next.js + shadcn/ui admin panel with auth, model browser, API key management, and provider controls
- **Two-layer audit logging** — HTTP request logs to stdout + structured usage/audit records persisted to the database

---

## Architecture

```
┌──────────────┐     ┌──────────────────────────────────┐
│  @piee/sdk   │────▶│  FastAPI Backend  (:8000)         │
│  TypeScript  │     │                                    │
└──────────────┘     │  /v1/chat/completions  (SSE)       │
                     │  /v1/embeddings                    │
┌──────────────┐     │  /v1/models                        │
│  Dashboard   │────▶│  /v1/ollama/*  (pull, sync, tags)  │
│  Next.js     │     │                                    │
│  :3000       │     │  RouterEngine → ProviderRegistry   │
└──────────────┘     │    ├── OpenAI Provider              │
                     │    ├── Anthropic Provider           │
                     │    └── Ollama Provider              │
                     └──────────────────────────────────┘
```

---

## Quick Start

### Method 1: Docker (Recommended)

The easiest way to run the full stack (API + Dashboard) is using Docker Compose:

```bash
cp .env.example .env
make docker-up
```

Access the dashboard at `http://localhost:3000` and the API at `http://localhost:8000`.

### Method 2: Make (Local Development)

You can run the stack locally using the provided `Makefile`:

```bash
cp .env.example .env
make setup   # Creates .env, Python .venv, installs Node deps, sets up DB
make dev     # Starts both API (8000) and Dashboard (3000) with hot-reloading
make start   # Production mode — builds Dashboard then starts both services
```

The backend runs inside a localized Python virtual environment (`.venv`). If you need to run Python commands manually, either activate it (`source .venv/bin/activate`) or use the binaries in `.venv/bin/`.

### Code Quality & Testing

```bash
make format  # Auto-format: Ruff (backend) + Prettier (frontend)
make lint    # Lint: Ruff + ESLint + Mypy
make test    # Run Pytest suite (backend)
```

*Run `make help` to see all available commands.*

### Method 3: Manual Startup

**1. Backend**
```bash
cp .env.example .env
pip3 install -r requirements.txt
python3 -m prisma generate
python3 -m prisma db push
python3 -m uvicorn app.main:app --port 8000
```

**2. Dashboard**
```bash
cd dashboard
npm install
npm run dev   # → http://localhost:3000
```

### SDK Example

```typescript
import PIEE from "@piee/sdk";

const piee = new PIEE({
  baseURL: "http://localhost:8000",
  apiKey: "pk-your-api-key",
});

// Standard completion
const response = await piee.chat.completions.create({
  model: "openai/gpt-4o",
  messages: [{ role: "user", content: "Hello!" }],
});

// Streaming
const stream = await piee.chat.completions.create({
  model: "openai/gpt-4o",
  messages: [{ role: "user", content: "Tell me a story." }],
  stream: true,
});
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}
```

---

## Dashboard Features

| Tab | What it does |
|-----|-------------|
| **Overview** | Usage stats, token counts, cost breakdown |
| **Models** | Browse all registered models across providers |
| **API Keys** | Create, view, and revoke API keys |
| **Providers** | Configure and test provider connections |
| **Ollama** | Pull models from Ollama Hub, sync to registry, view installed models |
| **Sandbox** | Full-page chat playground with streaming toggle, system prompt, temperature & max token sliders, and markdown rendering |
| **Usage** | Audit log of all API calls with latency and status codes |

---

## Sandbox Playground

The Sandbox tab provides a full-page interactive playground for testing models directly from the dashboard:

- **Streaming** — Toggle SSE token-by-token streaming on/off
- **System Prompt** — Customise the assistant's persona per session
- **Temperature** — Slider from 0 to 2
- **Max Tokens** — Slider from 128 to 8192
- **Markdown Rendering** — Assistant responses render code blocks, tables, lists, and more via `react-markdown` + `remark-gfm`

---

## Logging & Audit

PIEE uses a two-layer logging system:

**1. HTTP Request Logs (stdout)**
Every request is logged by `RequestLoggingMiddleware`:
```
23:18:46 | piee.audit | INFO | POST /v1/chat/completions → 200 (258ms) [127.0.0.1]
```

**2. Persistent Audit Records (database)**
Security-sensitive events (auth, billing, admin writes) and all model usage are persisted to the database:

- `UsageLog` — tokens in/out, cost, latency, model, user
- `AuditLog` — action, IP address, user agent, details

Inspect records with `make db-studio` (opens Prisma Studio at `http://localhost:5555`).

---

## Project Structure

```
PIEE/
├── app/                  # FastAPI backend
│   ├── main.py           # App entry point
│   ├── config.py         # Settings (Pydantic)
│   ├── dependencies.py   # Auth, DB, feature flags
│   ├── auth/             # JWT, API keys, encryption
│   ├── providers/        # BaseProvider + adapters (OpenAI, Anthropic, Ollama)
│   ├── router/           # RouterEngine + ModelRegistry
│   ├── api/              # OpenAI-compatible endpoints
│   ├── billing/          # Credit wallet (cloud)
│   ├── audit/            # Usage logging + middleware
│   └── flags/            # Feature flag system
├── sdk/                  # TypeScript SDK
├── dashboard/            # Next.js + shadcn/ui
│   └── src/app/page.tsx  # All dashboard pages (SPA)
├── prisma/               # Database schema
├── docker-compose.yml    # Docker services config
├── Dockerfile            # Backend multi-stage build
├── Makefile              # Helper commands
├── .env.example          # Environment template
└── requirements.txt      # Python dependencies
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_MODE` | `local` or `cloud` | `local` |
| `DATABASE_URL` | SQLite or PostgreSQL URL | `file:./dev.db` |
| `JWT_SECRET` | JWT signing secret | — |
| `ENCRYPTION_KEY` | Fernet key for API key encryption | — |
| `OPENAI_API_KEY` | OpenAI API key (optional) | — |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) | — |
| `LOCAL_INFERENCE_URL` | Ollama base URL | `http://localhost:11434` |
| `NEXT_PUBLIC_API_URL` | Backend URL for dashboard | `http://localhost:8000` |

---

## License

MIT
