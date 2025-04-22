from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_current_user
from domain.services.recommendation_service import RecommendationEngine
from api.schemas import RecommendationResponse

router = APIRouter(
    prefix="/recommendations",
    tags=["Персонализированные рекомендации мест"],
    dependencies=[Depends(get_current_user)]
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
    engine = RecommendationEngine(session)
    results = await engine.recommend(user_id=user.id, latitude=latitude, longitude=longitude)
    return {"results": results}
