from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from hotel_service.deps import get_hotel_repository
from hotel_service.repositories.hotel import HotelRepository
from hotel_service.schemas.hotel import HotelSearchRequest, HotelListResponse
from hotel_service.services.redis import RedisService
from settings import settings
from hotel_service.utils.logger import logger

logger.info("Приложение запущено")
logger.debug("Это отладочное сообщение")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = RedisService(settings.REDIS_URL)
    await redis.connect()
    app.state.redis = redis  # сохраняем в state
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)


@app.get("/hotels", response_model=HotelListResponse, tags=["Поиск и рекомендация отелей"])
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
):
    hotels = await repo.search_hotels(query)
    return {"results": hotels}

