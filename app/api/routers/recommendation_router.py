from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_current_user
from domain.services.recommendation_service import RecommendationEngine
from api.schemas import RecommendationResponse

router = APIRouter(
    prefix="/recommendations",
    tags=["Персонализированные рекомендации мест"],
)


@router.get(
    "/",
    response_model=RecommendationResponse,
    summary="Получить рекомендованные места"
)
async def get_recommendations(
        latitude: float,
        longitude: float,
        session: AsyncSession = Depends(get_db),
        user=Depends(get_current_user),
):
    """
    Получить рекомендованные места на основе предпочтений пользователя и его местоположения.

    :param latitude: Широта для поиска рекомендаций.
    :param longitude: Долгота для поиска рекомендаций.
    :param session: Сессия для работы с базой данных.
    :param user: Текущий авторизованный пользователь, чьи предпочтения будут использованы для генерации рекомендаций.

    :return: Список рекомендованных мест, основанных на истории и предпочтениях пользователя.
    :raises HTTPException: В случае возникновения ошибок при генерации рекомендаций.
    """
    engine = RecommendationEngine(session)
    results = await engine.recommend(user_id=user.id, latitude=latitude, longitude=longitude)
    return {"results": results}
