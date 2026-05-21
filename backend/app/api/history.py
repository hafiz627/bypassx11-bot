from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.history import HistoryItem
from app.db import get_session

router = APIRouter(prefix="/api", tags=["history"])

@router.get('/history')
async def history(session: AsyncSession = Depends(get_session)):
    rows = (await session.exec(select(HistoryItem).order_by(HistoryItem.created_at.desc()).limit(100))).all()
    return rows
