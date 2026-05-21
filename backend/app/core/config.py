from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Universal URL Resolver")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./resolver.db")
    allowed_origins: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    max_redirect_depth: int = int(os.getenv("MAX_REDIRECT_DEPTH", "8"))

settings = Settings()
