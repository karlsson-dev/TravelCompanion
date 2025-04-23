from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Visit
from api.schemas import VisitCreate


class VisitService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_visit(self, visit_data: VisitCreate) -> Visit:
        visit = Visit(**visit_data.model_dump())
        self.session.add(visit)
        await self.session.commit()
        await self.session.refresh(visit)
        return visit
