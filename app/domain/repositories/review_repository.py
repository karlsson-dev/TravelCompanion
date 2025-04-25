from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.api.schemas.review import ReviewCreate
from app.infrastructure.database.models.user_place_review import UserPlaceReview
from infrastructure.database.models import User


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, review_create: ReviewCreate) -> UserPlaceReview:
        try:
            new_review = UserPlaceReview(**review_create.model_dump())
            self.db.add(new_review)
            await self.db.commit()
            await self.db.refresh(new_review)
            return new_review
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при создании отзыва: {str(e)}")

    async def get_all_reviews(self):
        result = await self.db.execute(select(UserPlaceReview))
        return result.scalars().all()

    async def update_review(self, review_id: int, content: str, rating: int, user: User):
        try:
            result = await self.db.execute(
                select(UserPlaceReview).where(
                    UserPlaceReview.id == review_id,
                    UserPlaceReview.user_id == user.id
                )
            )
            review = result.scalar_one_or_none()
            if not review:
                raise HTTPException(
                    status_code=404,
                    detail="Отзыв с указанным ID не найден или не принадлежит текущему пользователю."
                )

            review.content = content
            review.rating = rating
            await self.db.commit()
            return review

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении отзыва: {str(e)}")

    async def delete_review(self, review_id: int):
        try:
            await self.db.execute(delete(UserPlaceReview).where(UserPlaceReview.id == review_id))
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении отзыва: {str(e)}")


    async def get_review_by_id(self, review_id: int, user: User):
        result = await self.db.execute(
            select(UserPlaceReview).where(UserPlaceReview.id == review_id and UserPlaceReview.user_id == user.id)
        )
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(
                status_code=404,
                detail="Отзыв с указанным ID не найден или не принадлежит текущему пользователю."
            )
        return review
