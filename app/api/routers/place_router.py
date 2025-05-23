from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from api.schemas import PlaceSchema, PlaceResponse
from infrastructure.database.models import CategoryEnum, Place, Rating, User
from utils.utils import get_local_places
from core.dependencies import get_db, get_current_user, get_nominatim_client
from domain.repositories import TripRepository
from infrastructure.external.foursquare_client import (search_places,
                                                       parse_place_item,
                                                       foursquare_category_id,
                                                       prepare_new_ratings)

router = APIRouter(
    prefix="/search",
    tags=["Поиск и рекомендация мест"],
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
    """
    Поиск мест по заданной категории, координатам, радиусу и минимальному рейтингу.

    :param category: Категория мест (например, рестораны, магазины).
    :param latitude: Широта для поиска мест.
    :param longitude: Долгота для поиска мест.
    :param radius: Радиус поиска в метрах.
    :param min_rating: Минимальный рейтинг для мест (по умолчанию нет фильтрации по рейтингу).
    :param db: Сессия для работы с базой данных.
    :param current_user: Текущий авторизованный пользователь, чьи предпочтения могут быть использованы для поиска.
    :return: Список мест, соответствующих запросу.
    :raises HTTPException 400: В случае некорректной категории для поиска.
    :raises HTTPException 401: Если пользователь не авторизован.
    :raises HTTPException 500: В случае ошибок при работе с базой данных или внешними сервисами.
    """
    category_id = foursquare_category_id(category)
    if not category_id:
        raise HTTPException(status_code=400, detail="Неверная категория для поиска")

    try:
        # Получаем данные мест из базы данных
        local_places = await get_local_places(db, latitude, longitude, radius, category.value, min_rating)
        if local_places:
            # Сохраняем информацию о поездке в таблице trips
            async with get_nominatim_client() as client:
                destination = await client.reverse_geocode(latitude, longitude)

            repo = TripRepository(db)
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

        # После сохранения мест в базе данных, сохраняем поездку
        async with get_nominatim_client() as client:
            destination = await client.reverse_geocode(latitude, longitude)

        repo = TripRepository(db)
        await repo.save_trip(current_user.id, destination,
                             category.value)

        return PlaceResponse(places=[PlaceSchema.model_validate(p) for p in places])

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {str(e)}")
