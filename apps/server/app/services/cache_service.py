import json
from redis.asyncio import Redis


async def get_cached(redis: Redis, key: str) -> dict | list | None:
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cache(redis: Redis, key: str, value, ttl: int = 600) -> None:
    await redis.setex(key, ttl, json.dumps(value, default=str))


async def delete_cache(redis: Redis, key: str) -> None:
    await redis.delete(key)


async def delete_pattern(redis: Redis, pattern: str) -> None:
    keys = []
    async for key in redis.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis.delete(*keys)


async def invalidate_post_caches(redis: Redis, slug: str | None = None) -> None:
    await delete_pattern(redis, "cache:posts:page:*")
    await delete_pattern(redis, "cache:tag:*")
    await delete_cache(redis, "cache:tags:all")
    if slug:
        await delete_cache(redis, f"post:summary:{slug}")


async def increment_counter(redis: Redis, key: str, ttl: int = 86400) -> int:
    v = await redis.incr(key)
    await redis.expire(key, ttl)
    return v


async def get_counter(redis: Redis, key: str) -> int:
    v = await redis.get(key)
    return int(v) if v else 0


async def add_to_sorted_set(redis: Redis, key: str, member: str, increment: int = 1) -> None:
    await redis.zincrby(key, increment, member)


async def get_top_from_sorted_set(redis: Redis, key: str, count: int = 10) -> list[tuple[str, float]]:
    result = await redis.zrevrange(key, 0, count - 1, withscores=True)
    return [(item[0], item[1]) for item in result]
