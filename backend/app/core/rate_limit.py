import time
from collections import defaultdict, deque

class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 60, per_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self._buckets[key]
        while bucket and now - bucket[0] > self.per_seconds:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True
