from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator
from place_service.places.models import CategoryEnum

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

        # Проверка диапазонов для каждого источника
        if source == "Foursquare":
            if not (0 <= rating <= 10):
                raise ValueError("Рейтинг для Foursquare должен быть в пределах от 0 до 10.")
        elif source == "2GIS":
            if not (1 <= rating <= 5):
                raise ValueError("Рейтинг для 2GIS должен быть в пределах от 1 до 5.")
        else:
            raise ValueError(f"Неизвестный источник рейтинга: {source}")

        return values
