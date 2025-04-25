from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class UserPlaceHistory(Base):
    """
    Модель, представляющая историю взаимодействия пользователя с местами.

    Атрибуты:
        id (int): Уникальный идентификатор записи.
        user_id (int): Идентификатор пользователя.
        place_id (str): Идентификатор места (внешний).
        place_name (str): Название места.
        category (str): Категория места.
        rating (float): Рейтинг, связанный с посещением.
        user (User): Ссылка на пользователя.
    """
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    place_id = Column(String, index=True)
    place_name = Column(String)
    category = Column(String)
    rating = Column(Float)

    user = relationship("User", backref="user_place_histories")
