from collections.abc import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


from hotel_service.database import async_session_maker
from settings import HOTEL_SERVICE_PORT

app = FastAPI()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            await session.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=HOTEL_SERVICE_PORT, reload=True)
