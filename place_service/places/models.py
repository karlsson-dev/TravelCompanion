from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class CategoryEnum(str, Enum):
    food = "13065"  # Restaurants
    entertainment = "10032"  # Entertainment & Events
    shopping = "17000"  # Shops & Retail
    attraction = "16000"  # Arts & Entertainment (достопримечательности)

    def __str__(self):
        """Переопределяем строковое представление, чтобы Swager отображал названия."""
        descriptions = {
            "13065": "Еда (Рестораны)",
            "10032": "Развлечения",
            "17000": "Шопинг",
            "16000": "Достопримечательности"
        }
        return descriptions[self.value]

class Location(BaseModel):
    lat: float
    lon: float

class Place(BaseModel):
    name: str
    location: Location
    address: Optional[str] = None
    rating: Optional[float]  # Рейтинг необязателен (может быть None)

class PlaceResponse(BaseModel):
    places: List[Place]

