# # Логика взаимодействия с API Foursquare
import requests, os
from dotenv import load_dotenv

load_dotenv()
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

FOURSQUARE_URL = "https://api.foursquare.com/v3/places/search"

headers = {
    "Authorization": FOURSQUARE_API_KEY,
    "Accept": "application/json"
}


def search_places(params):
    response = requests.get(FOURSQUARE_URL, headers=headers, params=params)
    response.raise_for_status()  # Проверка на ошибки
    return response.json()
