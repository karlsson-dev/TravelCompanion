from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    user_id: int = Field(..., description="ID пользователя, оставившего отзыв", ge=1)
    place_id: int = Field(..., description="ID места, на которое оставлен отзыв", ge=1)
    content: str = Field(..., description="Текст отзыва", min_length=5, max_length=1000)
    rating: int = Field(..., description="Оценка (1-5)", ge=1, le=5)

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int = Field(..., description="ID отзыва")
    user_id: int = Field(..., description="ID пользователя, оставившего отзыв")
    place_id: int = Field(..., description="ID места, на которое оставлен отзыв")
    content: str = Field(..., description="Текст отзыва")
    rating: int = Field(..., description="Оценка (1-5)")
    created_at: Optional[datetime] = Field(None, description="Дата и время создания отзыва")

    model_config = ConfigDict(from_attributes=True)
