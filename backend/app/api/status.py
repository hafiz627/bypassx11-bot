from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/api", tags=["status"])

@router.get("/status", response_model=HealthResponse)
async def status():
    return {"status": "ok", "version": "1.0.0"}
