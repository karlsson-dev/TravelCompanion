from fastapi import Depends
from functools import lru_cache
from services.redis import RedisService
from repositories.hotel import HotelRepository
from settings import settings


@lru_cache
def get_redis_service() -> RedisService:
    redis = RedisService(redis_url=settings.redis_url)
    return redis

async def get_redis(redis: RedisService = Depends(get_redis_service)) -> RedisService:
    if redis.redis is None:
        await redis.connect()
    return redis

def get_hotel_repository(
    redis: RedisService = Depends(get_redis),
) -> HotelRepository:
    return HotelRepository(api_key=settings.opentripmap_api_key, redis=redis)
