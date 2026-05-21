from sqlmodel import SQLModel, Field
from datetime import datetime

class HistoryItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    input_url: str
    final_url: str | None = None
    provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
