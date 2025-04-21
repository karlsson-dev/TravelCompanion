import math
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from infrastructure.database.models.place import Place, Rating


def get_bounding_box(lat: float, lon: float, radius_meters: int):
    """
    Грубая фильтрация по диапазону
    """
    earth_radius = 6378137  # радиус Земли в метрах
    delta_lat = radius_meters / earth_radius * (180 / math.pi)
    delta_lon = radius_meters / (earth_radius * math.cos(math.radians(lat))) * (180 / math.pi)
    return (
        lat - delta_lat, lat + delta_lat,
        lon - delta_lon, lon + delta_lon
    )


async def get_local_places(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    radius: int,
    category: str,
    min_rating: Optional[float] = None
) -> List[Place]:
    lat_min, lat_max, lon_min, lon_max = get_bounding_box(latitude, longitude, radius)

    stmt = select(Place).where(
        and_(
            Place.latitude.between(lat_min, lat_max),
            Place.longitude.between(lon_min, lon_max),
            Place.category == category,
            Place.external_id.isnot(None)
        )
    )
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    if not candidates:
        return []

    place_ids = [place.id for place in candidates]

    ratings_stmt = select(Rating.place_id, Rating.rating).where(
        Rating.place_id.in_(place_ids),
        Rating.source == "Foursquare"
    )
    ratings_result = await db.execute(ratings_stmt)
    rating_map = {row.place_id: row.rating for row in ratings_result}

    filtered_places = []
    for place in candidates:
        rating = rating_map.get(place.id)
        if min_rating is None or (rating is not None and rating >= min_rating):
            filtered_places.append(place)

    return filtered_places
