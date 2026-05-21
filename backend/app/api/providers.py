from fastapi import APIRouter
from app.engine.manager import EngineManager

router = APIRouter(prefix="/api", tags=["providers"])
engine = EngineManager()

@router.get('/providers')
async def providers():
    return engine.provider_catalog()
