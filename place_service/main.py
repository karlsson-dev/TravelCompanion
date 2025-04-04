from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Optional

from fastapi import Query, Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from place_service.apis.foursquare_api import search_places, foursquare_category_id
from place_service.database import async_session_maker
from place_service.places.models import CategoryEnum, Place, PlaceSchema, PlaceResponse, Rating

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
        raise HTTPException(status_code=400, detail="Invalid category")

    try:
        params = {
            "ll": f"{latitude},{longitude}",
            "radius": radius,
            "categories": category_id,
            "limit": 10
        }

        data = search_places(params=params)
        if not data.get("results"):
            return PlaceResponse(places=[])

        places = []
        new_places = []
        new_ratings = []
        external_ids = [item.get("fsq_id") for item in data["results"] if item.get("fsq_id")]

        existing_places_query = await db.execute(select(Place).where(Place.external_id.in_(external_ids)))
        existing_places = {place.external_id: place for place in existing_places_query.scalars()}

        for item in data["results"]:
            name = item.get("name")
            geocode = item.get("geocodes", {}).get("main")
            address = item.get("location", {}).get("formatted_address", "")
            rating = item.get("rating")
            external_id = item.get("fsq_id")

            if min_rating is not None and (rating is None or rating < min_rating):
                continue

            if name and geocode:
                if external_id in existing_places:
                    places.append(existing_places[external_id])
                else:
                    new_places.append({
                        "name": name,
                        "latitude": geocode["latitude"],
                        "longitude": geocode["longitude"],
                        "address": address,
                        "external_id": external_id,
                        "created_at": datetime.now(timezone.utc).replace(tzinfo=None),
                        "updated_at": datetime.now(timezone.utc).replace(tzinfo=None),
                    })

        if new_places:
            stmt = insert(Place).values(new_places).returning(Place.id, Place.external_id)
            result = await db.execute(stmt)
            inserted_places = {row.external_id: row.id for row in result.mappings()}

            for item in data["results"]:
                external_id = item.get("fsq_id")
                rating = item.get("rating")
                if external_id in inserted_places and rating is not None:
                    new_ratings.append({
                        "source": "Foursquare",
                        "rating": rating,
                        "place_id": inserted_places[external_id]
                    })

            for place in new_places:
                place["id"] = inserted_places[place["external_id"]]
                places.append(Place(**place))

        if new_ratings:
            await db.execute(insert(Rating).values(new_ratings))

        await db.commit()

        return PlaceResponse(places=[PlaceSchema.model_validate(place) for place in places])

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
