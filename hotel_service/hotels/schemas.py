from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


class SHotel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(..., min_length=1, max_length=100, description="Название отеля")
    address: str = Field(..., min_length=10, max_length=200, description="Адрес отеля")
    city: str = Field(..., min_length=2, max_length=100, description="Город, в котором находится отель")
    country: str = Field(..., min_length=2, max_length=100, description="Страна, в которой находится отель")
    latitude: float = Field(..., description="Широта отеля")
    longitude: float = Field(..., description="Долгота отеля")
    description: Optional[str] = Field(None, max_length=500, description="Описание отеля")
    star_rating: Optional[float] = Field(None, ge=0, le=5, description="Звездность отеля от 0 до 5")


class SHotelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=10, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    latitude: float
    longitude: float
    description: Optional[str] = Field(None, max_length=500)
    star_rating: Optional[float] = Field(None, ge=0, le=5)


class SReview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int = Field(..., ge=1, description="ID отеля")
    reviewer_name: str = Field(..., min_length=1, max_length=100, description="Имя рецензента")
    review_text: str = Field(..., min_length=10, max_length=1000, description="Текст отзыва")
    created_at: datetime = Field(..., description="Дата создания отзыва")


class SReviewCreate(BaseModel):
    hotel_id: int
    reviewer_name: str
    review_text: str


class SRating(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int = Field(..., ge=1)
    score: float = Field(..., ge=0, le=10, description="Оценка отеля от 0 до 10")
    source: str = Field(..., min_length=1, max_length=100, description="Источник рейтинга")


class SRatingCreate(BaseModel):
    hotel_id: int
    score: float
    source: str
