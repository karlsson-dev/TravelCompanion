from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends

from hotel_service.deps import get_hotel_repository, get_redis_service
from hotel_service.repositories.hotel import HotelRepository
from hotel_service.schemas.hotel import HotelSearchRequest, HotelListResponse
from settings import HOTEL_SERVICE_PORT
from hotel_service.utils.logger import logger

logger.info("Приложение запущено")
logger.debug("Это отладочное сообщение")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = get_redis_service()
    await redis.connect()
    yield
    if redis.redis:
        await redis.redis.close()


app = FastAPI(lifespan=lifespan)


@app.get("/hotels", response_model=HotelListResponse, tags=["Поиск и рекомендация отелей"])
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
):
    hotels = await repo.search_hotels(query)
    return {"results": hotels}




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=HOTEL_SERVICE_PORT, reload=True)

