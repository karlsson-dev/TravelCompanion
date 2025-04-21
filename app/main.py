from contextlib import asynccontextmanager
import time
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.cache.redis_service import RedisService
from core.logger import logger

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from core.config import settings, SERVICE_PORT
from api.routers import place_router, hotel_router, auth_router, user_router, trip_router

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

# --- ( кастомный Swagger, чтобы не передавать токен вручную каждый раз) ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(LoggingMiddleware)

app.include_router(place_router)
app.include_router(hotel_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(trip_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True)
