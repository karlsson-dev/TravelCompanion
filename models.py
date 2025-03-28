from enum import Enum
from pydantic import BaseModel
from typing import List


class CategoryEnum(str, Enum):
    food = "еда"
    entertainment = "развлечения"
    shopping = "магазин"
    attraction = "достопримечательности"


class Location(BaseModel):
    lat: float
    lon: float


class Place(BaseModel):
    name: str
    location: Location
    address: str


class PlaceResponse(BaseModel):
    places: List[Place]
