"""Redis Client — Shared async Redis connection for multi-worker support.

Provides a singleton async Redis connection pool used by the feature store
for cross-worker gallery synchronisation and pub/sub notifications.

Graceful fallback: if Redis is unreachable, all callers get None and
should degrade to single-worker (process-local) behaviour.
"""
import logging
from typing import Optional

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

# Singleton connection
_redis: Optional[aioredis.Redis] = None
_available: bool = False


async def init_redis() -> bool:
    """Initialise the async Redis connection pool.

    Returns True if Redis is reachable, False otherwise.
    """
    global _redis, _available

    settings = get_settings()
    try:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=False,  # we store binary numpy data
            socket_connect_timeout=3,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Verify connectivity
        await _redis.ping()
        _available = True
        logger.info(f"Redis connected: {settings.REDIS_URL}")
        return True

    except Exception as e:
        logger.warning(
            f"Redis unavailable ({e}) — falling back to single-worker mode. "
            f"Feature gallery will NOT sync across workers."
        )
        _redis = None
        _available = False
        return False


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global _redis, _available
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception:
            pass
        _redis = None
        _available = False
        logger.info("Redis connection closed")


def get_redis() -> Optional[aioredis.Redis]:
    """Return the shared Redis instance (or None if unavailable)."""
    return _redis


def is_redis_available() -> bool:
    """Check whether Redis is connected."""
    return _available
