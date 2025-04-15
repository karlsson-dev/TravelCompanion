from typing import Optional, Union
from aioredis import Redis, from_url
from loguru import logger
import json


class RedisService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        """
        Установить соединение с Redis.
        """
        try:
            self.redis = await from_url(self.redis_url, decode_responses=True)
            logger.info("Соединение с Redis установлено.")
        except Exception as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
            self.redis = None

    async def get(self, key: str) -> Optional[str]:
        """
        Получить значение из Redis по ключу.
        """
        try:
            if self.redis is None:
                logger.warning("Redis не подключён. Попытка автоподключения...")
                await self.connect()

            if self.redis is None:
                raise ConnectionError("Не удалось подключиться к Redis.")

            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Ошибка при получении ключа {key} из Redis: {e}")
            return None

    async def set(self, key: str, value: Union[str, dict], ttl: int = 3600) -> None:
        """
        Сохранить значение в Redis с TTL.
        """
        try:
            if self.redis is None:
                logger.warning("Redis не подключён. Попытка автоподключения...")
                await self.connect()

            if self.redis is None:
                raise ConnectionError("Не удалось подключиться к Redis.")

            if isinstance(value, dict):
                value = json.dumps(value)

            await self.redis.set(name=key, value=value, ex=ttl)
        except Exception as e:
            logger.error(f"Ошибка при сохранении ключа {key} в Redis: {e}")

    async def close(self) -> None:
        """
        Закрыть соединение с Redis.
        """
        if self.redis:
            try:
                await self.redis.close()
                logger.info("Соединение с Redis закрыто.")
            except Exception as e:
                logger.warning(f"Ошибка при закрытии Redis: {e}")
