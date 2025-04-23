from sqlalchemy import String, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base

# пользовательские отзывы
class UserPlaceReview(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    place_id = Column(Integer, ForeignKey('places.id'))
    content = Column(String)
    rating = Column(Integer)

    user = relationship('User', back_populates='user_reviews')
    place = relationship('Place', back_populates='user_reviews')