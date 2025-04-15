import httpx
from typing import List
from loguru import logger
from hotel_service.models.hotels import Hotel

class OpenTripMapClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def search_hotels(self, params: dict) -> List[Hotel]:
        """
        Запрос к OpenTripMap API для поиска отелей
        """
        url = f"{self.base_url}/ru/places/autosuggest"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка при запросе к OpenTripMap API: {e}")
            raise e
        except Exception as e:
            logger.error(f"Неизвестная ошибка при запросе к OpenTripMap API: {e}")
            raise e

    def parse_hotels(self, data: list) -> List[Hotel]:
        """
        Преобразует данные об отелях в объекты Hotel
        """
        hotels: List[Hotel] = []
        for item in data:
            try:
                hotel = Hotel(
                    name=item.get("name", ""),
                    dist=item.get("dist", 0.0),
                    rate=item.get("rate", 0),
                    lat=item["point"]["lat"],
                    lon=item["point"]["lon"]
                )
                hotels.append(hotel)
            except (KeyError, TypeError) as e:
                logger.warning(f"Ошибка при парсинге данных об отеле: {e}")
                continue
        if not hotels:
            logger.warning("Не удалось найти отели по данному запросу.")
        return hotels
