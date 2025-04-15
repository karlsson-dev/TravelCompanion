import httpx
import hashlib
import json
from typing import List

from loguru import logger
from aioredis.exceptions import ConnectionError

from hotel_service.models.hotels import Hotel
from hotel_service.schemas.hotel import HotelSearchRequest
from hotel_service.services.redis import RedisService


class HotelRepository:
    def __init__(
        self,
        redis: RedisService,
        opentripmap_api_key: str,
        opentripmap_url: str
    ):
        self.redis = redis
        self.opentripmap_api_key = opentripmap_api_key
        self.opentripmap_url = opentripmap_url


    def _build_cache_key(self, params: dict) -> str:
        """
        Генерация кэш-ключа на основе параметров запроса.
        """
        raw = json.dumps(params, sort_keys=True)
        return f"hotel:{hashlib.md5(raw.encode()).hexdigest()}"

    async def _fetch_hotels_from_api(self, params: dict) -> list[dict]:
        """
        Запрос к OpenTripMap API.
        """
        url = f"{self.opentripmap_url}/ru/places/autosuggest"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def search_hotels(self, query: HotelSearchRequest) -> List[Hotel]:
        params = {
            "name": query.name,
            "radius": query.radius,
            "lat": query.lat,
            "lon": query.lon,
            "rate": query.rate,
            "kinds": "accomodations",
            "format": "json",
            "apikey": self.opentripmap_api_key,
        }

        if query.sort_by:
            params["sort_by"] = query.sort_by

        cache_key = self._build_cache_key(params)
        data = None

        try:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info(f"Кэш найден по ключу: {cache_key}")
                data = json.loads(cached)
            else:
                logger.info("Запрос к OpenTripMap API...")
                logger.debug(f"Параметры запроса: {params}")
                data = await self._fetch_hotels_from_api(params)

                # Сохраняем в Redis с TTL = 300 секунд (5 минут)
                await self.redis.set(cache_key, json.dumps(data), ttl=300)
                logger.info("Данные сохранены в Redis.")
        except ConnectionError as e:
            logger.warning(f"Redis недоступен: {e}")
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")
            raise

        hotels: List[Hotel] = []

        for item in data:
            try:
                hotels.append(Hotel(
                    name=item.get("name", ""),
                    dist=item.get("dist", 0.0),
                    rate=item.get("rate", 0),
                    lat=item["point"]["lat"],
                    lon=item["point"]["lon"]
                ))
            except KeyError as e:
                logger.warning(f"Пропущен элемент из-за ошибки ключа: {e}")

        if query.sort_by == "distance":
            hotels.sort(key=lambda h: h.dist)
        elif query.sort_by == "rating":
            hotels.sort(key=lambda h: h.rate, reverse=True)

        return hotels
