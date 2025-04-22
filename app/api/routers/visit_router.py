from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_current_user
from api.schemas import RecommendationResponse, VisitResponse, VisitCreate
from domain.services.recommendation_service import RecommendationEngine
from domain.services.visit_service import VisitService
from typing import Any

router = APIRouter(prefix="/visits", tags=["История посещений"])


@router.post(
    "/",
    response_model=VisitResponse,
    dependencies=[Depends(get_current_user)]
)
async def create_visit(
        visit: VisitCreate,
        session: AsyncSession = Depends(get_db),
        user: Any = Depends(get_current_user),
):
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
