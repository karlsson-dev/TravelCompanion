import hashlib
import json
from typing import List

from loguru import logger
from aioredis.exceptions import ConnectionError

from domain.dto.hotel_dto import Hotel
from api.schemas.hotel import HotelSearchRequest
from infrastructure.cache.redis_service import RedisService
from infrastructure.external.opentripmap_client import OpenTripMapClient


class HotelRepository:
    def __init__(
            self,
            redis: RedisService,
            opentripmap_client: OpenTripMapClient
    ):
        self.redis = redis
        self.opentripmap_client = opentripmap_client

    def _build_cache_key(self, params: dict) -> str:
        """
        Генерация кэш-ключа на основе параметров запроса
        """
        raw = json.dumps(params, sort_keys=True)
        return f"hotel:{hashlib.md5(raw.encode()).hexdigest()}"

    async def search_hotels(self, query: HotelSearchRequest) -> List[Hotel]:
        params = {
            "name": query.name,
            "radius": query.radius,
            "lat": query.lat,
            "lon": query.lon,
            "rate": query.rate,
            "kinds": "accomodations",
            "format": "json",
            "apikey": self.opentripmap_client.api_key,
        }

        if query.sort_by:
            params["sort_by"] = query.sort_by

        cache_key = self._build_cache_key(params)
        data = None

        # Попытка получить данные из кэша Redis
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info(f"Кэш найден по ключу: {cache_key}")
                data = json.loads(cached)
            else:
                logger.info("Запрос к OpenTripMap API...")
                logger.debug(f"Параметры запроса: {params}")
                data = await self.opentripmap_client.search_hotels(params)

                try:
                    await self.redis.set(cache_key, json.dumps(data), ttl=300)
                except ConnectionError as e:
                    logger.warning(f"Redis недоступен при сохранении: {e}")
                except Exception as e:
                    logger.error(f"Ошибка при сохранении ключа {cache_key} в Redis: {e}")
        except ConnectionError as e:
            logger.warning(f"Redis недоступен при получении: {e}")
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")
            # Возвращаем пустой список в случае ошибки
            return []

        # Преобразуем данные в список объектов Hotel
        hotels = self.opentripmap_client.parse_hotels(data)

        # Сортируем по выбранному параметру
        if query.sort_by == "distance":
            hotels.sort(key=lambda h: h.dist)
        elif query.sort_by == "rating":
            hotels.sort(key=lambda h: h.rate, reverse=True)

        return hotels
