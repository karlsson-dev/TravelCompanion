from fastapi import Depends, Request
from services.redis import RedisService
from repositories.hotel import HotelRepository
from app.core.config import settings
from clients.opentripmap_client import OpenTripMapClient


async def get_redis(request: Request):
    return request.app.state.redis


def get_opentripmap_client() -> OpenTripMapClient:
    return OpenTripMapClient(
        api_key=settings.OPENTRIPMAP_API_KEY,
        base_url=settings.OPENTRIPMAP_URL
    )


def get_hotel_repository(
        redis: RedisService = Depends(get_redis),
        opentripmap_client: OpenTripMapClient = Depends(get_opentripmap_client)
) -> HotelRepository:
    return HotelRepository(
        redis=redis,
        opentripmap_client=opentripmap_client
    )
