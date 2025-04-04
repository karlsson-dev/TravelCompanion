import logging
import os
from typing import Dict, Any

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from httpx import Timeout

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


PRODUCTION_TIMEOUTS = {
    "connect": 3.0,  # Таймаут на установку соединения
    "read": 10.0,  # Таймаут на чтение ответа
    "write": 5.0,  # Таймаут на отправку запроса
    "pool": 2.0  # Таймаут ожидания свободного соединения из пула
}

CONNECTION_LIMITS = httpx.Limits(
    max_connections=100,  # Общий лимит соединений
    max_keepalive_connections=20  # Долгоживущие соединения
)


async def search_places(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Поиск мест через Foursquare API с обработкой ошибок и таймаутом
    """
    if not all([FOURSQUARE_API_KEY, FOURSQUARE_INTEGRATION_URL]):
        logger.error("Не настроены обязательные переменные окружения для Foursquare API")
        raise HTTPException(
            status_code=500,
            detail="Service configuration error"
        )

    timeout = Timeout(**PRODUCTION_TIMEOUTS)

    async with httpx.AsyncClient(
            timeout=timeout,
            limits=CONNECTION_LIMITS,
            transport=httpx.AsyncHTTPTransport(retries=2)  # 2 попытки ретрая
    ) as client:
        try:
            # Запрос с отдельным таймаутом для поиска (меньше чем read timeout)
            response = await client.get(
                FOURSQUARE_INTEGRATION_URL,
                headers=HEADERS,
                params=params,
                timeout=Timeout(8.0)
            )# Специфичный таймаут для этого API

            response.raise_for_status()
            return response.json()

        except httpx.ConnectTimeout:
            logger.error("Таймаут при запросе к Foursquare API")
            raise HTTPException(
                status_code=504,
                detail="Could not connect to Foursquare API"
            )

        except httpx.ReadTimeout:
            logger.error("Ошибка на чтение ответа Foursquare API")
            raise HTTPException(
                status_code=504,
                detail="Foursquare API response timeout"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка Foursquare API: {e.response.status_code}")
            raise HTTPException(
                status_code=502,
                detail=f"Foursquare API error: {e.response.text[:200]}..."
            )

        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса к Foursquare API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable"
            )

        except Exception as e:
            logger.error(f"Неожиданный запрос: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

