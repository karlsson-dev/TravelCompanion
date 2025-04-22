from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TripCreate(BaseModel):
    destination: str = Field(..., min_length=2)
    category: Optional[str] = None


class TripResponse(BaseModel):
    id: int
    destination: str
    category: Optional[str]
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
