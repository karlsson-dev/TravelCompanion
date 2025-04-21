from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from api.schemas import PlaceSchema, PlaceResponse

from infrastructure.external import FourSquareClient, NominatimClient
from infrastructure.database.models import CategoryEnum, Place, Rating, User
from utils.utils import get_local_places
from core.dependencies import get_db, get_current_user
from domain.repositories import TripRepository

router = APIRouter(
    prefix="/search",
    tags=["Поиск мест"],
    dependencies=[Depends(get_current_user)]  # авторизация для всех маршрутов
)

@router.get("/", summary="Получить места")
async def search_places_handler(
        category: CategoryEnum = Query(..., description="Категория мест"),
        latitude: float = Query(..., description="Широта"),
        longitude: float = Query(..., description="Долгота"),
        radius: int = Query(1000, description="Радиус поиска в метрах"),
        min_rating: Optional[float] = Query(None, description="Минимальный рейтинг (0-10)"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Получаем текущего пользователя
):
    category_id = FourSquareClient.foursquare_category_id(category)
    if not category_id:
        raise HTTPException(status_code=400, detail="Неверная категория для поиска")

    try:
        # Получаем данные мест из базы данных
        local_places = await get_local_places(db, latitude, longitude, radius, category.value, min_rating)
        if local_places:
            # Сохраняем информацию о поездке в таблице trips
            repo = TripRepository(db)
            destination = await NominatimClient.reverse_geocode(latitude, longitude)
            await repo.save_trip(current_user.id, destination,
                                 category.value)

            return PlaceResponse(places=[PlaceSchema.model_validate(p) for p in local_places])

        # Если не нашли — обращаемся к внешнему API
        params = {
            "ll": f"{latitude},{longitude}",
            "radius": radius,
            "categories": category_id,
            "limit": 10
        }
        data = await FourSquareClient.search_places(params=params)
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
            place_data = FourSquareClient.parse_place_item(item, min_rating)
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

            rating_values = FourSquareClient.prepare_new_ratings(ratings_buffer, inserted_places)
            if rating_values:
                await db.execute(insert(Rating).values(rating_values))

        await db.commit()

        # После сохранения мест в базе данных, сохраняем поездку
        repo = TripRepository(db)
        destination = await NominatimClient.reverse_geocode(latitude, longitude)
        await repo.save_trip(current_user.id, destination,
                             category.value)

        return PlaceResponse(places=[PlaceSchema.model_validate(p) for p in places])

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {str(e)}")
