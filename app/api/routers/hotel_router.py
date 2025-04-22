from fastapi import APIRouter, Depends, HTTPException
import time

from loguru import logger

from core.dependencies import get_hotel_repository
from domain.repositories import HotelRepository
from api.schemas import HotelSearchRequest



router = APIRouter (
    prefix="/hotels",
    tags=["Поиск и рекомендация отелей"],
    dependencies=[Depends(get_hotel_repository)], # авторизация для всех маршрутов
)

@router.get("/", summary="Получить отели")
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
):
    start = time.perf_counter()
    try:
        hotels = await repo.search_hotels(query)
        return {"results": hotels}
    except Exception as e:
        logger.error(f"Ошибка при получении отелей: {e}")
        raise HTTPException(status_code=503, detail="Сервис временно недоступен")
    finally:
        duration = time.perf_counter() - start
        logger.info(f"Время выполнения запроса /hotels: {duration:.3f} сек")