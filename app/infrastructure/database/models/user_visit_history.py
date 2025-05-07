from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class UserVisit(Base):
    """
    Модель факта посещения пользователем определённого места.

    Атрибуты:
        id (int): Уникальный идентификатор посещения.
        user_id (int): Идентификатор пользователя.
        external_id (str): Внешний ID места.
        name (str): Название места.
        latitude (float): Широта.
        longitude (float): Долгота.
        address (str): Адрес.
        category (Optional[str]): Категория места.
        user (User): Ссылка на пользователя.
    """
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    external_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    category = Column(String, nullable=True)

    user = relationship("User", backref="visits")
