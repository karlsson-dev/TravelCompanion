from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import relationship

from ..base import Base


class User(Base):
    """
    Модель пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Адрес электронной почты.
        hashed_password (str): Хэшированный пароль.
        user_reviews (List[UserPlaceReview]): Отзывы, оставленные пользователем.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    user_reviews = relationship("UserPlaceReview", back_populates="user", cascade="all, delete-orphan")
