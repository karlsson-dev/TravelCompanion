import json
import os
from fastapi import FastAPI, Query, HTTPException
from models import CategoryEnum, Place, Location, PlaceResponse
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

BASE_URL = "https://catalog.api.2gis.com/3.0/items"


@app.get("/places/", response_model=PlaceResponse)
def get_places(
        category: CategoryEnum = Query(..., description="Категория мест"),
        lat: float = Query(..., description="Широта"),
        lon: float = Query(..., description="Долгота"),
        radius: int = Query(1000, description="Радиус поиска в метрах"),
        sort: bool = Query(True, description="Сортировать по рейтингу"),
) -> PlaceResponse:
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")

    params = {
        "q": category,
        "key": API_KEY,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "fields": "items.point,items.name,items.address,items.has_rating, items.reviews",
    }

    if sort:
        params["sort"] = "rating"  # API сам выдаст отсортированный по рейтингу результат

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка API 2GIS")

    data = response.json()

    print(json.dumps(data, indent=2, ensure_ascii=False))  # смотрим ответ в консоль

    # Обрабатываем места из ответа
    places = []
    for item in data.get("result", {}).get("items", []):
        name = item.get("name")
        point = item.get("point")
        address_name = item.get("address_name")
        building_name = item.get("building_name")
        full_name = item.get("full_name")

        # Если `address_name` отсутствует, используем `building_name`, иначе `full_name`
        address = address_name or building_name or full_name or ""

        if name and point:
            places.append(
                Place(
                    name=name,
                    location=Location(lat=point["lat"], lon=point["lon"]),
                    address=address
                )
            )
        elif name:  # Если координат нет, используем координаты запроса
            places.append(
                Place(
                    name=name,
                    location=Location(lat=lat, lon=lon),
                    address=address
                )
            )

    return PlaceResponse(places=places)
