from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VisitCreate(BaseModel):
    user_id: int
    external_id: str
    name: str
    latitude: float
    longitude: float
    address: str
    category: Optional[str] = None


class VisitResponse(VisitCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
