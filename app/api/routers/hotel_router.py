from fastapi import APIRouter, Depends, HTTPException
import time

from loguru import logger

from core.dependencies import get_hotel_repository, get_current_user
from domain.repositories import HotelRepository
from api.schemas import HotelSearchRequest

router = APIRouter(
    prefix="/hotels",
    tags=["Поиск и рекомендация отелей"],
    dependencies=[Depends(get_current_user)],  # авторизация для всех маршрутов
)


@router.get("/", summary="Получить отели")
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
):
    """
    Получить список отелей, соответствующих поисковому запросу.

    :param query: Параметры поиска отелей (категория, местоположение, рейтинг и т.д.).
    :param repo: Репозиторий отелей, отвечающий за взаимодействие с базой данных или внешними сервисами.

    :return: Список отелей, удовлетворяющих запросу.
    :raises HTTPException: Если произошла ошибка при получении данных отелей, возвращается код ошибки 503 (Сервис недоступен).
    """
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
