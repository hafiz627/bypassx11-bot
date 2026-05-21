from pydantic import BaseModel, HttpUrl, Field

class BypassRequest(BaseModel):
    urls: list[HttpUrl] = Field(default_factory=list)
    follow_redirects: bool = True
    max_depth: int = 8

class ResolvedResult(BaseModel):
    input_url: str
    final_url: str | None = None
    provider: str
    mime_type: str | None = None
    file_size: int | None = None
    safety_status: str = "unknown"
    trace: list[str] = []
    error: str | None = None

class BypassResponse(BaseModel):
    results: list[ResolvedResult]
