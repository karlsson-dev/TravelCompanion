from contextlib import asynccontextmanager
import time
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from core.dependencies import get_current_user
from infrastructure.cache.redis_service import RedisService
from core.logger import logger
from core.config import settings, SERVICE_PORT
from api.routers import *
from infrastructure.database.models import User

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


app = FastAPI(
    title="TravelCompanion API",
    description="API для поиска мест, отелей и персональных рекомендаций",
    version="1.0.0",
    lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

# Мокаем авторизацию
if settings.USE_FAKE_AUTH:
    async def fake_get_current_user() -> User:
        return User(id=1, username="devuser", email="dev@example.com")


    app.dependency_overrides[get_current_user] = fake_get_current_user

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(hotel_router)
app.include_router(place_router)
app.include_router(recommendation_router)
app.include_router(trip_router)
app.include_router(user_router)
app.include_router(visit_router)
app.include_router(review_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True)
