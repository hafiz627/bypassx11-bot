import asyncio
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.api import BypassRequest, BypassResponse
from app.core.security import sanitize_url
from app.core.rate_limit import InMemoryRateLimiter
from app.engine.manager import EngineManager
from app.models.history import HistoryItem
from app.db import get_session

router = APIRouter(prefix="/api", tags=["bypass"])
engine = EngineManager()
rate_limiter = InMemoryRateLimiter()

@router.post("/bypass", response_model=BypassResponse)
async def bypass_urls(payload: BypassRequest, request: Request, session: AsyncSession = Depends(get_session)):
    ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    urls = []
    for u in payload.urls:
        try:
            urls.append(sanitize_url(str(u)))
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err

    async def _run(url: str):
        for _ in range(2):
            try:
                return await engine.resolve_one(url, payload.max_depth)
            except Exception as e:
                last = {"input_url": url, "provider": "unknown", "error": str(e), "trace": []}
        return last

    results = await asyncio.gather(*[_run(u) for u in urls])

    for r in results:
        session.add(HistoryItem(input_url=r["input_url"], final_url=r.get("final_url"), provider=r.get("provider", "unknown")))
    await session.commit()
    return {"results": results}
