from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import TripCreate, TripResponse
from domain.repositories import TripRepository
from core.dependencies import get_db, get_current_user
from infrastructure.database.models import User
from typing import List

router = APIRouter(
    prefix="/trips",
    tags=["Поездки"],
    dependencies=[Depends(get_db), Depends(get_current_user)] # авторизация для всех маршрутов
)

@router.get("/", response_model=List[TripResponse])
async def list_user_trips(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    repo = TripRepository(db)
    return await repo.get_user_trips(user.id)
