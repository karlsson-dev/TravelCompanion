from typing import Optional, Union
from aioredis import Redis, from_url


class RedisService:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        """
        Установить соединение с Redis.
        """
        self.redis = await from_url(self.redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        """
        Получить значение из Redis по ключу.
        """
        if self.redis is None:
            raise ConnectionError("Redis не подключён")
        return await self.redis.get(key)

    async def set(self, key: str, value: Union[str, dict], ttl: int = 3600) -> None:
        """
        Сохранить значение в Redis с TTL.
        """
        if self.redis is None:
            raise ConnectionError("Redis не подключён")

        if isinstance(value, dict):
            import json
            value = json.dumps(value)

        await self.redis.set(name=key, value=value, ex=ttl)

    async def close(self) -> None:
        """
        Закрыть соединение с Redis.
        """
        if self.redis:
            await self.redis.close()

