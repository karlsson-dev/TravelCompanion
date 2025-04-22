from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_current_user
from api.schemas import RecommendationResponse, VisitResponse, VisitCreate
from typing import Any

from domain.services.recommendation_service import RecommendationEngine
from domain.services.visit_service import VisitService

from infrastructure.database.models import User

router = APIRouter(prefix="/visits", tags=["История посещений"])


@router.post(
    "/",
    response_model=VisitResponse,
    dependencies=[Depends(get_current_user)]
)
async def create_visit(
        visit: VisitCreate,
        session: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Создать запись о посещении места.

    Создает новую запись о посещении в базе данных для текущего пользователя.

    :param visit: Объект VisitCreate, содержащий информацию о посещенном месте.
    :param session: Объект базы данных (Session).
    :param user: Текущий авторизованный пользователь.

    :return: Созданная запись о посещении в формате VisitResponse.
    """
    service = VisitService(session)
    visit.user_id = user.id
    return await service.create_visit(visit)


@router.post(
    "/visited/",
    summary="История посещений",
    dependencies=[Depends(get_current_user)]
)
async def save_visited_place(
        place: RecommendationResponse,
        session: AsyncSession = Depends(get_db),
        user: Any = Depends(get_current_user),
):
    """
    Сохранить информацию о посещенном месте.
    Записывает информацию о месте, которое пользователь отметил как посещенное.
    :param place: Объект RecommendationResponse с данными о месте, которое было посещено.
    :param session: Объект базы данных (Session).
    :param user: Текущий авторизованный пользователь.
    :return: Сообщение о успешной записи.
    :raises HTTPException: В случае ошибки при сохранении информации о посещенном месте.
    """
    engine = RecommendationEngine(session)
    try:
        await engine.mark_as_visited(user_id=user.id, recommendation=place.model_dump())
        return {"message": "Place marked as visited"}
    except Exception as e:
        print(f"Error while marking place as visited: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while marking place as visited"
        )
