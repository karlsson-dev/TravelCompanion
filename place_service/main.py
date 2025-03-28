# Основной файл запуска FastAPI для работы с местами
from typing import Optional
from place_service.db import create_table, save_place
from fastapi import Query, FastAPI
from place_service.models import CategoryEnum, Place, Location, PlaceResponse
from place_service.foursquare_api import search_places

app = FastAPI()

# Создание таблицы при старте приложения
create_table()
@app.get("/search", response_model=PlaceResponse)
def search_places_endpoint(
        category: CategoryEnum = Query(..., description="Категория мест"),
        latitude: float = Query(..., description="Широта"),
        longitude: float = Query(..., description="Долгота"),
        radius: int = Query(1000, description="Радиус поиска в метрах"),
        min_rating: Optional[float] = Query(None, description="Минимальный рейтинг (0-10)"),
) -> PlaceResponse:
    params = {
        "ll": f"{latitude},{longitude}",
        "radius": radius,
        "categories": category.value,
        "limit": 10
    }

    data = search_places(params=params)

    places = []
    for item in data.get("results", []):
        name = item.get("name")
        geocode = item.get("geocodes", {}).get("main")
        address = item.get("location", {}).get("formatted_address", "")
        rating = item.get("rating", None)

        if min_rating is not None and (rating is None or rating < min_rating):
            continue  # Пропускаем места с низким рейтингом

        if name and geocode:
            place = Place(
                name=name,
                location=Location(lat=geocode["latitude"], lon=geocode["longitude"]),
                address=address,
                rating=rating,
            )
            places.append(place)

            # Сохраняем в БД
            save_place(
                name=name,
                address=address,
                category=category.name,
                rating=rating,
                latitude=geocode["latitude"],
                longitude=geocode["longitude"]
            )

    return PlaceResponse(places=places)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
