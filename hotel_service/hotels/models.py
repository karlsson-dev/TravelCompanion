from typing import List

from sqlalchemy import String, Float, ForeignKey, Text, DateTime, func, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from hotel_service.database import Base, int_pk

class Hotel(Base):
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0)

    ratings: Mapped[List["Rating"]] = relationship("Rating", back_populates="hotel", cascade="all, delete")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="hotel", cascade="all, delete")

    __table_args__ = (
        Index("idx_latitude", "latitude"),
        Index("idx_longitude", "longitude"),
    )

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"id={self.id!r}, "
                f"name={self.name!r}, "
                f"address={self.address!r}, "
                f"lat={self.latitude!r}, "
                f"lon={self.longitude!r})")


class Rating(Base):
    id: Mapped[int_pk]
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(100))  # например, "Amadeus", "Google"
    value: Mapped[float] = mapped_column(Float)

    hotel = relationship("Hotel", back_populates="ratings")

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"id={self.id!r}, "
                f"hotel_id={self.hotel_id!r}, "
                f"source={self.source!r}, "
                f"rating={self.value!r})")

class Review(Base):
    id: Mapped[int_pk]
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), index=True)
    author: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    hotel = relationship("Hotel", back_populates="reviews")
