import logging
import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
FOURSQUARE_INTEGRATION_URL = os.getenv("FOURSQUARE_URL")

DEFAULT_TIMEOUT = (3, 10)  # 3s на соединение, 10s на чтение
HEADERS = {
    "Authorization": FOURSQUARE_API_KEY,
    "Accept": "application/json"
}

# список предустановленных категорий
_CODE_MAPPING = {
    "Restaurants": "13065",
    "Entertainment & Events": "10032",
    "Shops & Retail": "17000",
    "Arts & Entertainment": "16000",
}


def foursquare_category_id(category):
    """Возвращает ID категории Foursquare API для данного значения"""
    return _CODE_MAPPING[category]


def search_places(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Поиск мест через Foursquare API с обработкой ошибок и таймаутом
    Args:
        params: Параметры запроса к API
    Returns:
        Ответ API в формате JSON
    Raises:
        requests.exceptions.RequestException: При ошибках запроса
        ValueError: При отсутствии обязательных переменных окружения
    """
    if not all([FOURSQUARE_API_KEY, FOURSQUARE_INTEGRATION_URL]):
        raise ValueError("Не настроены обязательные переменные окружения для Foursquare API")

    try:
        response = requests.get(
            FOURSQUARE_INTEGRATION_URL,
            headers=HEADERS,
            params=params,
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе к Foursquare API")
        raise
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP ошибка: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Ошибка запроса: {req_err}")
        raise
    except ValueError as json_err:
        logger.error(f"Ошибка парсинга JSON: {json_err}")
        raise
