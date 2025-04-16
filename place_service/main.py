from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Optional

import uvicorn
from fastapi import Query, Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from place_service.apis.foursquare_api import search_places, foursquare_category_id, parse_place_item, \
    prepare_new_ratings
from place_service.database import async_session_maker
from place_service.places.models import CategoryEnum, Place, Rating
from place_service.places.schemas import PlaceSchema, PlaceResponse
from place_service.utils import get_local_places
from settings import PLACE_SERVICE_PORT

app = FastAPI()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            await session.close()


@app.get("/search", response_model=PlaceResponse)
async def search_places_handler(
        category: CategoryEnum = Query(..., description="Категория мест"),
        latitude: float = Query(..., description="Широта"),
        longitude: float = Query(..., description="Долгота"),
        radius: int = Query(1000, description="Радиус поиска в метрах"),
        min_rating: Optional[float] = Query(None, description="Минимальный рейтинг (0-10)"),
        db: AsyncSession = Depends(get_db)
):
    category_id = foursquare_category_id(category)
    if not category_id:
        raise HTTPException(status_code=400, detail="Неверная категория для поиска")

    try:
        local_places = await get_local_places(db, latitude, longitude, radius, category.value, min_rating)
        if local_places:
            return PlaceResponse(places=[PlaceSchema.model_validate(p) for p in local_places])

        # Если не нашли — обращаемся к внешнему API
        params = {
            "ll": f"{latitude},{longitude}",
            "radius": radius,
            "categories": category_id,
            "limit": 10
        }
        data = await search_places(params=params)
        results = data.get("results", [])
        if not results:
            return PlaceResponse(places=[])

        external_ids = [item.get("fsq_id") for item in results if item.get("fsq_id")]
        existing_places_query = await db.execute(select(Place).where(Place.external_id.in_(external_ids)))
        existing_places = {place.external_id: place for place in existing_places_query.scalars()}

        places = []
        new_places = []
        ratings_buffer = []

        for item in results:
            place_data = parse_place_item(item, min_rating)
            if not place_data:
                continue

            ext_id = place_data["external_id"]
            if ext_id in existing_places:
                places.append(existing_places[ext_id])
            else:
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                place_data["created_at"] = now
                place_data["updated_at"] = now
                place_data["category"] = category.value  # <-- добавляем категорию
                new_places.append(place_data)

                if place_data.get("rating") is not None:
                    ratings_buffer.append({
                        "source": "Foursquare",
                        "rating": place_data["rating"],
                        "external_id": ext_id,
                    })

        if new_places:
            stmt = insert(Place).values(new_places).returning(Place.id, Place.external_id)
            result = await db.execute(stmt)
            inserted_places = {row.external_id: row.id for row in result.mappings()}

            for place in new_places:
                place["id"] = inserted_places.get(place["external_id"])
                places.append(Place(**place))

            rating_values = prepare_new_ratings(ratings_buffer, inserted_places)
            if rating_values:
                await db.execute(insert(Rating).values(rating_values))

        await db.commit()
        return PlaceResponse(places=[PlaceSchema.model_validate(p) for p in places])

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PLACE_SERVICE_PORT, reload=True)