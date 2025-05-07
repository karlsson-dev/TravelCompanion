from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from api.schemas import UserResponse
from infrastructure.database.models import User

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе.

    :param current_user: Текущий авторизованный пользователь.

    :return: Объект UserResponse с информацией о текущем пользователе.
    :raises HTTPException 401: Если пользователь не авторизован.
    """
    return current_user
