from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

_cache: dict[tuple[str, tuple[Any, ...], tuple[tuple[str, Any], ...]], tuple[float, Any]] = {}
_lock = threading.Lock()


def caching_enabled() -> bool:
    return os.getenv("ENABLE_CACHING", "false").lower() in ("1", "true", "yes")


def cached(ttl: int = 10) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        key_prefix = f"{fn.__module__}.{fn.__name__}"

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not caching_enabled():
                return fn(*args, **kwargs)
            key = (key_prefix, args, tuple(sorted(kwargs.items())))
            now = time.time()
            with _lock:
                if key in _cache:
                    expire, value = _cache[key]
                    if now < expire:
                        return value
            value = fn(*args, **kwargs)
            with _lock:
                _cache[key] = (now + ttl, value)
            return value

        return wrapper

    return decorator
