from dataclasses import dataclass

@dataclass
class ResolveContext:
    url: str
    max_depth: int = 8

class ProviderHandler:
    name = "base"
    domains: list[str] = []

    async def resolve(self, ctx: ResolveContext):
        raise NotImplementedError
