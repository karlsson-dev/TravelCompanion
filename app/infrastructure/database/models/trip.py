from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..base import Base


class Trip(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    destination = Column(String, nullable=False)
    category = Column(String, nullable=True)  # еда / шопинг / достопримечательности

    user = relationship("User", backref="trips")
