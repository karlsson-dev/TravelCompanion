from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import TripResponse
from domain.repositories import TripRepository
from core.dependencies import get_db, get_current_user
from infrastructure.database.models import User
from typing import List

router = APIRouter(
    prefix="/trips",
    tags=["Поездки"],
)


@router.get("/", response_model=List[TripResponse])
async def list_user_trips(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Получить список поездок пользователя.

    :param db: Сессия для работы с базой данных.
    :param user: Текущий авторизованный пользователь, чьи поездки будут получены.

    :return: Список поездок пользователя в виде объектов TripResponse.
    :raises HTTPException: В случае ошибок при запросе поездок пользователя из базы данных.
    """
    repo = TripRepository(db)
    return await repo.get_user_trips(user.id)
