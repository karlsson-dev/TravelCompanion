from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base


class UserTrip(Base):
    """
    Модель пользовательской поездки.

    Атрибуты:
        id (int): Уникальный идентификатор поездки.
        user_id (int): Идентификатор пользователя.
        destination (str): Пункт назначения.
        category (Optional[str]): Категория предпочтений (еда, шопинг, достопримечательности).
        user (User): Ссылка на пользователя.
    """
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    destination = Column(String, nullable=False)
    category = Column(String, nullable=True)  # еда / шопинг / достопримечательности

    user = relationship("User", backref="trips")
