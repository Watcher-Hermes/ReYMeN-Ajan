# -*- coding: utf-8 -*-
"""
cache_manager — Thread-safe in-memory cache with TTL support.

Features:
  - Per-key time-to-live (TTL)
  - Optional max size (evicts LRU when full)
  - Decorator @cached for easy function result caching
  - Global singleton (global_cache) for ad-hoc use
  - Pure Python, no external dependencies

Kullanim:
    from reymen.core import CacheManager, cached, global_cache

    cache = CacheManager(ttl=60, maxsize=1000)
    cache.set("anahtar", {"data": 42})
    val = cache.get("anahtar")

    @cached(ttl=30)
    def expensive_func(x):
        return x * x
"""

import time
import threading
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Optional


class CacheManager:
    """Thread-safe in-memory cache with TTL and LRU eviction.

    Args:
        ttl: Default time-to-live in seconds (default: 60).
        maxsize: Maximum number of entries (default: 1000, 0 = unlimited).
    """

    def __init__(self, ttl: int = 60, maxsize: int = 1000):
        self._ttl = ttl
        self._maxsize = maxsize
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()

    # ── Temel Islemler ────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key. Returns *default* if missing or expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return default
            val, expiry = entry
            if expiry is not None and time.monotonic() > expiry:
                del self._store[key]
                return default
            # LRU: move to end (most recently used)
            self._store.move_to_end(key)
            return val

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value with optional per-key TTL override.

        Args:
            key: Cache key (must be str).
            value: Any picklable object.
            ttl: Override TTL in seconds. None = use instance default.
        """
        expiry = None
        t = ttl if ttl is not None else self._ttl
        if t > 0:
            expiry = time.monotonic() + t
        with self._lock:
            self._store[key] = (value, expiry)
            self._store.move_to_end(key)
            self._evict_if_needed()

    def delete(self, key: str) -> bool:
        """Remove a key. Returns True if it existed."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._store.clear()

    # ── Bilgi Metodlari ────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        """Number of entries (including expired ones, cleaned lazily)."""
        with self._lock:
            return len(self._store)

    def keys(self) -> list[str]:
        """Return all non-expired keys."""
        with self._lock:
            now = time.monotonic()
            return [k for k, (_, e) in self._store.items()
                    if e is None or now <= e]

    def stats(self) -> dict:
        """Return usage statistics."""
        with self._lock:
            now = time.monotonic()
            expired = sum(1 for _, (_, e) in self._store.items()
                          if e is not None and now > e)
            return {
                "size": len(self._store),
                "expired": expired,
                "maxsize": self._maxsize,
                "ttl": self._ttl,
            }

    # ── String Representation ────────────────────────────────────────────────

    def __str__(self) -> str:
        """User-friendly string: CacheManager(size=3/1000 ttl=60s)"""
        return f"CacheManager(size={self.size}/{self._maxsize} ttl={self._ttl}s)"

    def __repr__(self) -> str:
        return f"CacheManager(ttl={self._ttl}, maxsize={self._maxsize})"

    # ── Yardimci ────────────────────────────────────────────────────────────

    def _evict_if_needed(self) -> None:
        """Evict oldest entries when over maxsize."""
        if self._maxsize <= 0:
            return
        while len(self._store) > self._maxsize:
            self._store.popitem(last=False)  # FIFO eviction

    def _clean_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        now = time.monotonic()
        expired_keys = [
            k for k, (_, e) in self._store.items()
            if e is not None and now > e
        ]
        for k in expired_keys:
            del self._store[k]
        return len(expired_keys)


# ── Decorator ────────────────────────────────────────────────────────────────

def cached(ttl: Optional[int] = None, maxsize: int = 1000):
    """Decorator: cache function return values with TTL.

    Args:
        ttl: Cache TTL in seconds (default: use caller default).
        maxsize: Max cache entries (default: 1000).

    Kullanim:
        @cached(ttl=30)
        def fetch_data(url: str) -> dict:
            return expensive_api_call(url)
    """
    caches: dict[Callable, CacheManager] = {}

    def decorator(func: Callable) -> Callable:
        mgr = CacheManager(ttl=ttl or 60, maxsize=maxsize)
        caches[func] = mgr

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Build string key from args/kwargs
            parts = [str(a) for a in args]
            parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = ":".join(parts)
            # Check
            cached_val = mgr.get(key)
            if cached_val is not None:
                return cached_val
            # Compute
            result = func(*args, **kwargs)
            mgr.set(key, result)
            return result

        wrapper.cache_clear = mgr.clear        # type: ignore[attr-defined]
        wrapper.cache_info = mgr.stats          # type: ignore[attr-defined]
        return wrapper

    return decorator


# ── Global Singleton ─────────────────────────────────────────────────────────

global_cache = CacheManager(ttl=120, maxsize=500)
"""Global cache instance. Ad-hoc kullanim icin:
    from reymen.core import global_cache
    global_cache.set("key", value)
    val = global_cache.get("key")
"""
