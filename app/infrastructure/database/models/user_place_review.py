from sqlalchemy import String, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base

class UserPlaceReview(Base):
    """
    Модель пользовательского отзыва на место.

    Атрибуты:
        id (int): Уникальный идентификатор отзыва.
        user_id (int): Идентификатор пользователя.
        place_id (int): Идентификатор места.
        content (str): Текст отзыва.
        rating (int): Оценка отзыва (1-5).
        user (User): Ссылка на пользователя.
        place (Place): Ссылка на место.
    """
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    place_id = Column(Integer, ForeignKey('places.id'))
    content = Column(String)
    rating = Column(Integer)

    user = relationship('User', back_populates='user_reviews')
    place = relationship('Place', back_populates='user_reviews')