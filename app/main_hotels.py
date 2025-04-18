from contextlib import asynccontextmanager
import time

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.dependencies import get_hotel_repository
from app.domain.repositories.hotel import HotelRepository
from app.api.schemas.hotel import HotelSearchRequest, HotelListResponse
from app.infrastructure.cache.redis_service import RedisService
from app.core.config import settings, HOTEL_SERVICE_PORT
from app.core.logger import logger

logger.info("Приложение запущено")
logger.debug("Это отладочное сообщение")


# Логирование всех HTTP-запросов — метод, путь, статус-код, время выполнения и IP клиента
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000  # в миллисекундах

        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} "
            f"({process_time:.2f}ms) от {client_ip}"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = RedisService(settings.REDIS_URL)
    try:
        await redis.connect()
        # сохраняем в state
        app.state.redis = redis
        logger.info("Redis подключён")
        yield
    finally:
        await redis.close()
        logger.info("Redis соединение закрыто")


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggingMiddleware)


@app.get("/hotels", response_model=HotelListResponse, tags=["Поиск и рекомендация отелей"])
async def get_hotels(
        query: HotelSearchRequest = Depends(),
        repo: HotelRepository = Depends(get_hotel_repository),
):
    start = time.perf_counter()
    try:
        hotels = await repo.search_hotels(query)
    except Exception as e:
        logger.error(f"Ошибка при получении отелей: {e}")
        raise HTTPException(status_code=503, detail="Сервис временно недоступен")
    elapsed = time.perf_counter() - start

    return {"results": hotels}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=HOTEL_SERVICE_PORT, reload=True)