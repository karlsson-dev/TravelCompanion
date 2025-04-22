from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models import UserPlaceHistory


class UserHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_history(self, user_id: int):
        result = await self.session.execute(
            select(UserPlaceHistory).where(UserPlaceHistory.user_id == user_id)
        )
        return result.scalars().all()
