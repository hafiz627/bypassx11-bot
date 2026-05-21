from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.db import init_db, get_session
from app.api.bypass import router as bypass_router
from app.api.status import router as status_router
from app.api.history import router as history_router
from app.api.providers import router as providers_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(status_router)
app.include_router(providers_router)
app.include_router(history_router, dependencies=[Depends(get_session)])
app.include_router(bypass_router, dependencies=[Depends(get_session)])

@app.get("/")
async def root():
    return {"name": settings.app_name}
