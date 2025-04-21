import httpx

class NominatimClient:
    async def reverse_geocode(lat: float, lon: float) -> str:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "json",
            "lat": lat,
            "lon": lon,
            "zoom": 10,  # уровень детализации: 10 — город
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": "TravelCompanion/1.0"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("display_name", f"{lat}, {lon}")
