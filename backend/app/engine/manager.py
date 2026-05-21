from urllib.parse import urlparse
from app.engine.providers.base import ResolveContext, ProviderHandler
from app.engine.providers.generic import GenericHandler
from app.engine.providers.tinyurl import TinyUrlHandler

class EngineManager:
    def __init__(self):
        self.handlers: list[ProviderHandler] = [TinyUrlHandler(), GenericHandler()]

    def pick(self, url: str) -> ProviderHandler:
        domain = urlparse(url).netloc.lower()
        for h in self.handlers:
            if "*" in h.domains:
                continue
            if any(domain.endswith(d) for d in h.domains):
                return h
        return next(h for h in self.handlers if h.name == "generic")

    async def resolve_one(self, url: str, max_depth: int):
        handler = self.pick(url)
        return await handler.resolve(ResolveContext(url=url, max_depth=max_depth))

    def provider_catalog(self):
        return [{"name": h.name, "domains": h.domains, "enabled": True} for h in self.handlers]
