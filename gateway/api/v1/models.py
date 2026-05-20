from fastapi import APIRouter

from gateway.providers.registry import provider_registry

router = APIRouter(prefix="/v1", tags=["models"])


@router.get("/models")
async def models():
    return {"object": "list", "data": provider_registry.list_models()}

