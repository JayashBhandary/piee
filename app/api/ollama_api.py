"""
PIEE — Ollama Provider Management API

Provides specific endpoints for interacting with the local Ollama daemon,
allowing users to pull models, check connection status, and list available
Ollama models directly from the UI.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.dependencies import get_db, get_current_user
from app.providers.registry import ProviderRegistry
from app.router.service import ModelRegistryService

logger = logging.getLogger("piee.api.ollama")
router = APIRouter(prefix="/v1/ollama", tags=["Ollama Controls"])

# Need to instantiate a registry or pass it.
# To keep it simple, we initialize a bare provider registry just to get the config,
# or we directly instantiate OllamaProvider, or just use httpx to the default URL.
# Because Ollama API is mostly stateless HTTP calls, we can just construct an async client.

def get_ollama_base_url(settings: Settings = Depends(get_settings)) -> str:
    # Extract base url from environment configuration
    return settings.ollama_base_url

@router.get("/status")
async def check_connection(
    base_url: str = Depends(get_ollama_base_url),
    user=Depends(get_current_user)
):
    """Check if the local Ollama daemon is running."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{base_url}/")
            if resp.status_code == 200:
                return {"status": "online", "message": resp.text}
            else:
                return {"status": "offline", "message": "Ollama is not responding correctly."}
    except Exception as e:
        return {"status": "offline", "message": f"Connection failed: {str(e)}"}

@router.get("/models")
async def list_local_models(
    base_url: str = Depends(get_ollama_base_url),
    user=Depends(get_current_user)
):
    """List all models currently installed in the local Ollama daemon."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return {"status": "success", "models": data.get("models", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list local Ollama models: {str(e)}")

@router.post("/pull")
async def pull_model(
    payload: Dict[str, Any],
    base_url: str = Depends(get_ollama_base_url),
    user=Depends(get_current_user)
):
    """
    Tell Ollama to pull a specific model from its library.
    Expects JSON: {"name": "model-name"}
    Streams progress back to the client.
    """
    model_name = payload.get("name")
    if not model_name:
        raise HTTPException(status_code=400, detail="Model 'name' is required.")
        
    async def stream_generator():
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST", 
                    f"{base_url}/api/pull",
                    json={"name": model_name, "stream": True}
                ) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": f"Failed to pull model: {str(e)}"}).encode("utf-8")

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

@router.post("/sync")
async def sync_model_to_piee(
    payload: Dict[str, Any],
    db=Depends(get_db),
    base_url: str = Depends(get_ollama_base_url),
    user=Depends(get_current_user)
):
    """
    Takes an Ollama model name, verifies it locally, and records it in PIEE's 
    ModelRegistry so it becomes available in Sandbox and via OpenAI-compatible endpoints.
    Expects JSON: {"name": "model-name"}
    """
    model_name = payload.get("name")
    if not model_name:
        raise HTTPException(status_code=400, detail="Model 'name' is required.")

    # 1. Verify model exists in Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            models = resp.json().get("models", [])
            matches = [m for m in models if m["name"] == model_name or m["name"] == f"{model_name}:latest"]
            if not matches:
                raise HTTPException(status_code=404, detail=f"Model {model_name} not found in local Ollama instance.")
            ollama_model = matches[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify model in Ollama: {str(e)}")
        
    # 2. Add to PIEE registry
    from app.router.service import ModelRegistryService
    from app.router.models import ModelRegistryCreate
    
    # We prefix with ollama/ to match existing convention
    internal_id = f"ollama/{ollama_model['name']}"
    
    existing = await ModelRegistryService.get_model(db, internal_id)
    if existing:
        return {"status": "success", "message": "Model is already synced."}
        
    await ModelRegistryService.create_model(
        db,
        ModelRegistryCreate(
            model_id=internal_id,
            display_name=ollama_model['name'],
            provider="ollama",
            routing_mode="LOCAL",
            capabilities=["chat"],
            context_window=4096,
            input_price_per_m=0,
            output_price_per_m=0,
            is_active=True,
            is_premium=False
        )
    )
    
    return {"status": "success", "message": f"Synced {model_name} to PIEE Registry as {internal_id}"}
