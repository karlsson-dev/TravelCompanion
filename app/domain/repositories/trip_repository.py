from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from infrastructure.database.models import UserTrip


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_trip(self, user_id: int, destination: str, category: str = None) -> UserTrip:
        try:
            trip = UserTrip(user_id=user_id, destination=destination, category=category)
            self.db.add(trip)
            await self.db.commit()
            await self.db.refresh(trip)
            return trip
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных при сохранении поездки: {str(e)}")

    async def get_user_trips(self, user_id: int):
        stmt = select(UserTrip).where(UserTrip.user_id == user_id).order_by(UserTrip.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
