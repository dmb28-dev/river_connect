import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def publish_event(channel: str, data: dict[str, Any]) -> None:
    redis = await get_redis()
    await redis.publish(channel, json.dumps(data, default=str))


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
