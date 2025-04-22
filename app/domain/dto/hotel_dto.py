from dataclasses import dataclass


@dataclass
class Hotel:
    """
    DTO-модель отеля, получаемого от внешнего API.

    Attributes:
        name: Название отеля.
        dist: Расстояние от точки запроса в метрах.
        rate: Уровень известности отеля (от 1 до 3, h - культурное наследие).
        lat: Широта координат отеля.
        lon: Долгота координат отеля.
    """
    name: str
    dist: float
    rate: int
    lat: float
    lon: float
