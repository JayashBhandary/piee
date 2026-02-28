<p align="center">
  <img src="dashboard/assets/logo.png" width="80" alt="PIEE Logo" />
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
- **Unified SDK** — TypeScript SDK that works identically across local and cloud
- **Feature flags** — Premium features gated by deployment mode
- **Credit wallet** — Usage-based billing (cloud only, unlimited in local)
- **Dashboard** — Next.js + shadcn/ui admin panel with auth, model browser, API key management

---

## Architecture

```
┌──────────────┐     ┌──────────────────────────────────┐
│  @piee/sdk   │────▶│  FastAPI Backend  (:8000)         │
│  TypeScript  │     │                                    │
└──────────────┘     │  /v1/chat/completions              │
                     │  /v1/embeddings                    │
┌──────────────┐     │  /v1/models                        │
│  Dashboard   │────▶│                                    │
│  Next.js     │     │  RouterEngine → ProviderRegistry   │
│  :3000       │     │    ├── OpenAI Provider              │
└──────────────┘     │    ├── Anthropic Provider           │
                     │    └── Local/Ollama Provider        │
                     └──────────────────────────────────┘
```

---

## Quick Start

### 1. Backend

```bash
cd PIEE
cp .env.example .env
pip3 install -r requirements.txt
python3 -m prisma generate
python3 -m prisma db push
python3 -m uvicorn app.main:app --port 8000
```

### 2. Dashboard

```bash
cd dashboard
bun install   # or npm install
bun run dev   # → http://localhost:3000
```

### 3. SDK

```typescript
import PIEE from "@piee/sdk";

const piee = new PIEE({
  baseURL: "http://localhost:8000",
  apiKey: "pk-your-api-key",
});

const response = await piee.chat.completions.create({
  model: "openai/gpt-4o",
  messages: [{ role: "user", content: "Hello!" }],
});
```

---

## Project Structure

```
PIEE/
├── app/                  # FastAPI backend
│   ├── main.py           # App entry point
│   ├── config.py         # Settings (Pydantic)
│   ├── dependencies.py   # Auth, DB, feature flags
│   ├── auth/             # JWT, API keys, encryption
│   ├── providers/        # BaseProvider + adapters
│   ├── router/           # RouterEngine + ModelRegistry
│   ├── api/              # OpenAI-compatible endpoints
│   ├── billing/          # Credit wallet (cloud)
│   ├── audit/            # Usage logging + middleware
│   └── flags/            # Feature flag system
├── sdk/                  # TypeScript SDK
├── dashboard/            # Next.js + shadcn/ui
├── prisma/               # Database schema
├── .env.example          # Environment template
└── requirements.txt      # Python dependencies
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_MODE` | `local` or `cloud` | `local` |
| `DATABASE_URL` | SQLite or PostgreSQL | `file:./dev.db` |
| `JWT_SECRET` | JWT signing secret | — |
| `ENCRYPTION_KEY` | Fernet key for API key encryption | — |
| `OPENAI_API_KEY` | OpenAI API key (optional) | — |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) | — |
| `LOCAL_INFERENCE_URL` | Ollama URL | `http://localhost:11434` |

---

## License

MIT
