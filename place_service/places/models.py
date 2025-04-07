from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy import ForeignKey, Text, String, Numeric, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from place_service.database import Base, int_pk, str_null_true


class CategoryEnum(str, Enum):
    """Категории мест с ID Foursquare API"""
    FOOD = "Restaurants"  # 13065
    ENTERTAINMENT = "Entertainment & Events"  # 10032
    SHOPPING = "Shops & Retail"  # 17000
    ATTRACTION = "Arts & Entertainment"  # 16000


class Place(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    address: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str_null_true]  # ID из внешнего API
    ratings: Mapped[List["Rating"]] = relationship("Rating", back_populates="place")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="place")

    __table_args__ = (
        Index("idx_latitude", "latitude"),
        Index("idx_longitude", "longitude"),
    )

    def __str__(self):
        return (f"Место: {self.name}\n"
                f"Координаты: {self.latitude} {self.longitude}\n"
                f"Адрес: {self.address}\n")

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"id={self.id!r}, "
                f"name={self.name!r}, "
                f"external_id={self.external_id!r}, "
                f"lat={self.latitude!r}, "
                f"lon={self.longitude!r})")


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

class Rating(Base):
    id: Mapped[int_pk]
    source: Mapped[str] = mapped_column(String(50), unique=False)  # Название API (Foursquare, 2GIS и т. д.)
    rating: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)  # Для числовых оценок
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"), nullable=False)
    place: Mapped["Place"] = relationship("Place", back_populates="ratings")

    def __str__(self):
        return f"Рейтинг {self.rating} от {self.source}"

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"id={self.id!r}, "
                f"place_id={self.place_id!r}, "
                f"source={self.source!r}, "
                f"rating={self.rating!r})")


class Review(Base):
    id: Mapped[int_pk]
    source: Mapped[str] = mapped_column(String(50), unique=False)  # Название API (Foursquare, 2GIS и т. д.)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    place_id: Mapped[int] = mapped_column(
        ForeignKey("places.id"),
        nullable=False,
        index=True
    )
    place: Mapped["Place"] = relationship("Place", back_populates="reviews")
