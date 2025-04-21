from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, Request, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.cache.redis_service import RedisService
from domain.repositories import HotelRepository
from infrastructure.external import OpenTripMapClient
from infrastructure.database.base import async_session_maker
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError, jwt
from infrastructure.database.models import User
from sqlalchemy import select

from .config import settings, oauth2_scheme


async def get_redis(request: Request):
    return request.app.state.redis


@asynccontextmanager
async def get_opentripmap_client():
    client = OpenTripMapClient(
        api_key=settings.OPENTRIPMAP_API_KEY,
        base_url=settings.OPENTRIPMAP_URL
    )
    try:
        yield client
    finally:
        await client.close()


@asynccontextmanager
async def get_nominatim_client():
    client = OpenTripMapClient(
        api_key=settings.OPENTRIPMAP_API_KEY,
        base_url=settings.OPENTRIPMAP_URL
    )
    try:
        yield client
    finally:
        await client.close()


async def get_hotel_repository(
        redis: RedisService = Depends(get_redis),
        opentripmap_client: OpenTripMapClient = Depends(get_opentripmap_client)
) -> HotelRepository:
    return HotelRepository(
        redis=redis,
        opentripmap_client=opentripmap_client
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            await session.close()


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise credentials_exception

    return user
