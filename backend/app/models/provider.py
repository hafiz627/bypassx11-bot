from pydantic import BaseModel

class ProviderInfo(BaseModel):
    name: str
    domains: list[str]
    enabled: bool = True
