import httpx
import hashlib
import json

from loguru import logger
from typing import List

from hotel_service.models.hotels import Hotel
from hotel_service.schemas.hotel import HotelSearchRequest
from hotel_service.services.redis import RedisService


class HotelRepository:
    def __init__(self, api_key: str, redis: RedisService):
        self.api_key = api_key
        self.redis = redis
        self.base_url = "https://api.opentripmap.com/0.1"

    def _build_cache_key(self, params: dict) -> str:
        # Хешируем параметры запроса, чтобы получить ключ
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
            "apikey": self.api_key,
        }

        cache_key = self._build_cache_key(params)
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info("Кэш найден по ключу: {}", cache_key)
            data = json.loads(cached)
        else:
            logger.info("Отправка запроса к OpenTripMap")
            url = f"{self.base_url}/ru/places/autosuggest"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            await self.redis.set(cache_key, json.dumps(data))
            logger.info("Ответ сохранён в Redis")

        hotels = []
        for item in data:
            hotels.append(Hotel(
                name=item["name"],
                dist=item["dist"],
                rate=item["rate"],
                lat=item["point"]["lat"],
                lon=item["point"]["lon"]
            ))

        return hotels
