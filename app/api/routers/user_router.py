from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from api.schemas import UserResponse
from infrastructure.database.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)] # авторизация для всех маршрутов
)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
