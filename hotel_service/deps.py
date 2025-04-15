import os
from fastapi import Depends
from functools import lru_cache
from services.redis import RedisService
from repositories.hotel import HotelRepository
from settings import settings


@lru_cache
def get_redis_service() -> RedisService:
    redis = RedisService(redis_url=settings.REDIS_URL)
    return redis


async def get_redis(redis: RedisService = Depends(get_redis_service)) -> RedisService:
    if redis.redis is None:
        await redis.connect()
    return redis


def get_hotel_repository(
        redis: RedisService = Depends(get_redis),
) -> HotelRepository:
    return HotelRepository(
        redis=redis,
        opentripmap_api_key=settings.OPENTRIPMAP_API_KEY,
        opentripmap_url=settings.OPENTRIPMAP_URL
    )
