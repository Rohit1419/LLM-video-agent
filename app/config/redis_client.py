import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL" or "redis://localhost:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def get_redis_client():
    return redis_client
