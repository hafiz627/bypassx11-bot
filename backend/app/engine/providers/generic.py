import httpx
from app.engine.providers.base import ProviderHandler, ResolveContext
from app.engine.strategies import recursive_trace, head_probe

class GenericHandler(ProviderHandler):
    name = "generic"
    domains = ["*"]

    async def resolve(self, ctx: ResolveContext):
        async with httpx.AsyncClient(timeout=20) as client:
            final, trace = await recursive_trace(client, ctx.url, ctx.max_depth)
            head_url, mime, size = await head_probe(client, final)
            return {
                "input_url": ctx.url,
                "final_url": str(head_url),
                "provider": self.name,
                "mime_type": mime,
                "file_size": int(size) if size and size.isdigit() else None,
                "safety_status": "unverified",
                "trace": trace,
            }
