"""In-memory sliding-window rate limiter (single backend process).

State is lost on restart, which only makes the limiter more lenient for a
moment; it is a defence against brute force / abuse, not an accounting system.
"""
from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from typing import Callable, Hashable, Optional


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window_seconds
        self.clock = clock
        self._hits: dict = defaultdict(deque)

    def _prune(self, key: Hashable, now: float) -> deque:
        hits = self._hits[key]
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        return hits

    def retry_after(self, key: Hashable) -> Optional[int]:
        """Seconds to wait if ``key`` is over the limit, else None. Does not count a hit."""
        now = self.clock()
        hits = self._prune(key, now)
        if len(hits) >= self.limit:
            return max(1, math.ceil(self.window - (now - hits[0])))
        return None

    def hit(self, key: Hashable) -> Optional[int]:
        """Count a hit. Returns None if allowed, else the Retry-After in seconds (hit not counted)."""
        wait = self.retry_after(key)
        if wait is not None:
            return wait
        self._hits[key].append(self.clock())
        self._gc()
        return None

    def record(self, key: Hashable) -> None:
        """Count an event unconditionally (e.g. a failure)."""
        self._prune(key, self.clock()).append(self.clock())
        self._gc()

    def _gc(self) -> None:
        if len(self._hits) > 50_000:
            now = self.clock()
            for k in [k for k, v in self._hits.items() if not v or now - v[-1] >= self.window]:
                del self._hits[k]
