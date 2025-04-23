from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class Visit(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    external_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    category = Column(String, nullable=True)

    user = relationship("User", backref="visits")
