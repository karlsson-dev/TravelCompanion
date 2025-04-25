from fastapi import APIRouter, Depends, HTTPException, status
import time

from loguru import logger

from core.dependencies import get_hotel_repository, get_current_user
from domain.repositories import HotelRepository
from api.schemas import HotelSearchRequest
from infrastructure.database.models import User

router = APIRouter(
    prefix="/hotels",
    tags=["Поиск и рекомендация отелей"],
)


@router.get("/", summary="Получить отели")
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
        user: User = Depends(get_current_user),
):
    """
    Получить список отелей, соответствующих поисковому запросу.

    :param query: Параметры поиска отелей (категория, местоположение, рейтинг и т.д.).
    :param repo: Репозиторий отелей, отвечающий за взаимодействие с базой данных или внешними сервисами.
    :param user: Обёртка-заглушка для мока OAUTH2.
    :return: Список отелей, удовлетворяющих запросу.
    :raises HTTPException 401: Если пользователь не авторизован.
    :raises HTTPException 503: Если произошла ошибка при получении данных отелей.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

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
