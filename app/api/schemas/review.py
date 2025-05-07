from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ReviewCreate(BaseModel):
    user_id: int = Field(..., description="ID пользователя, оставившего отзыв", ge=1)
    place_id: int = Field(..., description="ID места, на которое оставлен отзыв", ge=1)
    content: str = Field(..., description="Текст отзыва", min_length=5, max_length=1000)
    rating: int = Field(..., description="Оценка (1-5)", ge=1, le=5)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": 1,
                "place_id": 1,
                "content": "Отличное место, всем рекомендую!",
                "rating": 5
            }
        }
    )

class ReviewResponse(BaseModel):
    id: int = Field(..., description="ID отзыва")
    user_id: int = Field(..., description="ID пользователя, оставившего отзыв")
    place_id: int = Field(..., description="ID места, на которое оставлен отзыв")
    content: str = Field(..., description="Текст отзыва")
    rating: int = Field(..., ge=1, le=5, description="Оценка (1-5)")
    created_at: datetime = Field(None, description="Дата и время создания отзыва")
    updated_at: datetime = Field(None, description="Дата и время последнего обновления отзыва")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "place_id": 1,
                "content": "Отличное место!",
                "rating": 5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )