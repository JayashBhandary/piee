"""
PIEE — OpenAI-Compatible Models Endpoint

GET /v1/models
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import ModelListResponseSchema, ModelSchema
from app.config import Settings, get_settings
from app.dependencies import get_db
from app.router.service import ModelRegistryService

router = APIRouter(prefix="/v1", tags=["Models"])


@router.get("/models", response_model=ModelListResponseSchema)
async def list_models(
    provider: str = None,
    settings: Settings = Depends(get_settings),
    db=Depends(get_db),
):
    """
    OpenAI-compatible model listing.
    Returns all active models from the ModelRegistry.
    """
    records = await ModelRegistryService.list_models(
        db, active_only=True, provider=provider
    )

    models = ModelRegistryService.to_openai_format(records)

    return ModelListResponseSchema(
        data=[
            ModelSchema(
                id=m.id,
                created=m.created,
                owned_by=m.owned_by,
            )
            for m in models
        ]
    )
