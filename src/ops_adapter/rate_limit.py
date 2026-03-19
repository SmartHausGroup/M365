from __future__ import annotations

import threading
import time
from collections import defaultdict


class TokenBucket:
    def __init__(self, rate_per_sec: float, burst: int):
        self.rate = rate_per_sec
        self.capacity = max(1, burst)
        self.tokens: float = float(self.capacity)
        self.timestamp = time.monotonic()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class RateLimiter:
    def __init__(self, default_rps: float = 5.0, burst: int = 10):
        self.default_rps = default_rps
        self.burst = burst
        self.buckets: dict[str, TokenBucket] = defaultdict(lambda: TokenBucket(default_rps, burst))

    def allow(self, key: str) -> bool:
        return self.buckets[key].allow()
