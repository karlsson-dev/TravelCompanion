from dataclasses import dataclass

@dataclass
class Hotel:
    """
    DTO-модель отеля, получаемого от внешнего API.
    """
    name: str           # Название отеля
    dist: float         # Расстояние от точки запроса в метрах
    rate: int           # Уровень известности отеля (от 1 до 3, h - культурное наследие)
    lat: float          # Широта координат отеля
    lon: float          # Долгота координат отеля
