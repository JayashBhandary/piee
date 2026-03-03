"""
PIEE — FastAPI Application Entry Point

Registers all routers, middleware, startup/shutdown events.
Supports both local and cloud deployment modes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logger = logging.getLogger("piee")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()
    logger.info(f"🚀 PIEE starting in {settings.deployment_mode.value.upper()} mode")

    # Initialize database
    try:
        from prisma import Prisma

        db = Prisma()
        await db.connect()

        # Seed default models
        from app.router.service import ModelRegistryService

        seeded = await ModelRegistryService.seed_defaults(db)
        if seeded > 0:
            logger.info(f"📦 Seeded {seeded} default models into registry")

        await db.disconnect()
    except Exception as e:
        logger.warning(f"⚠️  Database initialization: {e}")

    # Initialize provider registry
    try:
        from app.providers.registry import ProviderRegistry

        registry = ProviderRegistry(settings)
        await registry.initialize()
        providers = registry.list_providers()
        logger.info(f"🔌 Providers loaded: {', '.join(providers)}")
    except Exception as e:
        logger.warning(f"⚠️  Provider initialization: {e}")

    logger.info(f"✅ PIEE ready — http://{settings.host}:{settings.port}/docs")

    yield

    logger.info("👋 PIEE shutting down")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title="PIEE",
        description=(
            "Hybrid AI Infrastructure Platform — "
            "OpenAI-compatible API gateway with local and cloud deployment support."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"]
        if settings.is_local
        else [
            "https://piee.app",
            "https://dashboard.piee.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request Logging Middleware ──────────────
    from app.audit.middleware import RequestLoggingMiddleware

    app.add_middleware(RequestLoggingMiddleware)

    # ── Routers ─────────────────────────────────
    from app.auth.router import router as auth_router
    from app.api.chat import router as chat_router
    from app.api.embeddings import router as embeddings_router
    from app.api.models_api import router as models_router
    from app.billing.router import router as billing_router
    from app.audit.router import router as audit_router

    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(embeddings_router)
    app.include_router(models_router)
    app.include_router(billing_router)
    app.include_router(audit_router)

    # ── Health Check ───────────────────────────
    @app.get("/health", tags=["System"])
    async def health():
        return {
            "status": "healthy",
            "mode": settings.deployment_mode.value,
            "version": "0.1.0",
        }

    @app.get("/", tags=["System"])
    async def root():
        return {
            "name": "PIEE",
            "description": "Hybrid AI Infrastructure Platform",
            "version": "0.1.0",
            "mode": settings.deployment_mode.value,
            "docs": "/docs",
        }

    return app


# ── Module-level app instance for uvicorn ──────
app = create_app()

# ── Logging Configuration ──────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-15s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
