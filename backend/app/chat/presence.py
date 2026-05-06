import redis.asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None

ONLINE_TTL = 300
ONLINE_KEY_PREFIX = "user:online:"
RATE_KEY_PREFIX = "user:msgrate:"
RATE_LIMIT = 30
RATE_WINDOW = 60


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def set_online(user_id: int) -> None:
    r = await get_redis()
    await r.set(f"{ONLINE_KEY_PREFIX}{user_id}", "1", ex=ONLINE_TTL)


async def refresh_online(user_id: int) -> None:
    r = await get_redis()
    await r.expire(f"{ONLINE_KEY_PREFIX}{user_id}", ONLINE_TTL)


async def set_offline(user_id: int) -> None:
    r = await get_redis()
    await r.delete(f"{ONLINE_KEY_PREFIX}{user_id}")


async def is_online(user_id: int) -> bool:
    r = await get_redis()
    return await r.exists(f"{ONLINE_KEY_PREFIX}{user_id}") == 1


async def check_rate_limit(user_id: int) -> bool:
    r = await get_redis()
    key = f"{RATE_KEY_PREFIX}{user_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, RATE_WINDOW)
    return count <= RATE_LIMIT
