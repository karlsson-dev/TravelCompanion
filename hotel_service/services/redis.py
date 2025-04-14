import aioredis
from typing import Optional


class RedisService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        await self.redis.set(key, value, ex=expire)

    async def close(self):
        """Закрыть соединение с Redis."""
        if self.redis:
            await self.redis.close()
