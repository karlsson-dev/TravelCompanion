from pydantic import BaseModel, Field, ConfigDict
from typing import List


class HotelSearchRequest(BaseModel):
    """
    Схема запроса на поиск отелей.
    """
    name: str = Field(..., min_length=3, description="Текст для поиска в имени отеля (минимум 3 символа)")
    radius: int = Field(..., gt=0, description="Радиус поиска в метрах")
    lat: float = Field(..., description="Широта точки поиска")
    lon: float = Field(..., description="Долгота точки поиска")
    rate: int = Field(..., ge=1, le=3, description="Минимальный рейтинг известности (1 - мин, 3 - макс)")

    model_config = ConfigDict(from_attributes=True)


class HotelResponse(BaseModel):
    """
    Схема ответа с информацией об отеле.
    """
    name: str = Field(..., description="Название отеля")
    dist: float = Field(..., description="Расстояние до отеля от точки поиска в метрах")
    rate: int = Field(..., description="Рейтинг известности отеля")
    lat: float = Field(..., description="Широта отеля")
    lon: float = Field(..., description="Долгота отеля")

    model_config = ConfigDict(from_attributes=True)


class HotelListResponse(BaseModel):
    """
    Схема ответа с результатами поиска — список отелей.
    """
    results: List[HotelResponse]
