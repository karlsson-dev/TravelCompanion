from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class SortByEnum(str, Enum):
    distance = "distance"
    rating = "rating"

class HotelSearchRequest(BaseModel):
    """
    Схема запроса на поиск отелей.
    """
    name: str = Field(..., min_length=3, title="Имя отеля", description="Название отеля для поиска (минимум 3 символа)")
    radius: int = Field(..., gt=0, title="Радиус", description="Радиус поиска в метрах")
    lat: float = Field(..., title="Широта", description="Широта точки поиска")
    lon: float = Field(..., title="Долгота", description="Долгота точки поиска")
    rate: int = Field(..., ge=1, le=3, title="Рейтинг", description="Минимальный рейтинг отеля (от 1 до 3)")
    sort_by: Optional[SortByEnum] = Field(None, title="Сортировка",
                                          description="Параметр для сортировки результатов: по расстоянию или по рейтингу")
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
