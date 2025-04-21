from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator
from infrastructure.database.models.place import CategoryEnum

RATING_RANGES = {
    "Foursquare": (0, 10),
    "2GIS": (1, 5),
}

# Pydantic-модель для Place (DTO)
class PlaceSchema(BaseModel):
    id: Optional[int] = None
    name: str
    latitude: float
    longitude: float
    address: str
    external_id: Optional[str]
    category: CategoryEnum

    model_config = ConfigDict(from_attributes=True)  # для конвертации SQLAlchemy → Pydantic


class PlaceResponse(BaseModel):
    places: List[PlaceSchema]


class RatingSchema(BaseModel):
    id: Optional[int] = None
    source: str
    rating: float

    @model_validator(mode='before')
    def validate_rating_range(cls, values):
        source = values.get('source')
        rating = values.get('rating')

        if source not in RATING_RANGES:
            raise ValueError(f"Неизвестный источник рейтинга: {source}")

        min_rating, max_rating = RATING_RANGES[source]
        if not (min_rating <= rating <= max_rating):
            raise ValueError(
                f"Рейтинг для {source} должен быть в пределах от {min_rating} до {max_rating}."
            )

        return values
