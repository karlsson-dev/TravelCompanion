from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.api.schemas.review import ReviewCreate
from app.infrastructure.database.models.user_place_review import UserPlaceReview
from infrastructure.database.models import User


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        """Инициализация репозитория для работы с отзывами.

        Args:
            db: Асинхронная сессия SQLAlchemy для работы с базой данных
        """
        self.db = db

    async def create_review(self, review_create: ReviewCreate) -> UserPlaceReview:
        """Создает новый отзыв в базе данных.

        Args:
            review_create: Данные для создания отзыва

        Returns:
            Созданный объект отзыва

        Raises:
            HTTPException: При ошибках работы с базой данных
        """
        try:
            new_review = UserPlaceReview(**review_create.model_dump())
            self.db.add(new_review)
            await self.db.commit()
            await self.db.refresh(new_review)
            return new_review
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при создании отзыва: {str(e)}")

    async def get_all_reviews(self, limit: int = 100, offset: int = 0) -> list[UserPlaceReview]:
        """Получает список отзывов с пагинацией.

        Args:
            limit: Максимальное количество возвращаемых отзывов
            offset: Количество отзывов для пропуска

        Returns:
            Список объектов отзывов
        """
        result = await self.db.execute(
            select(UserPlaceReview)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_reviews_count(self) -> int:
        """Получает общее количество отзывов в базе.

        Returns:
            Общее количество отзывов
        """
        result = await self.db.execute(select(func.count()).select_from(UserPlaceReview))
        return result.scalar()

    async def update_review(self, review_id: int, content: str, rating: int, user: User) -> UserPlaceReview:
        """Обновляет существующий отзыв.

        Args:
            review_id: ID отзыва для обновления
            content: Новый текст отзыва
            rating: Новая оценка (1-5)
            user: Пользователь, которому принадлежит отзыв

        Returns:
            Обновленный объект отзыва

        Raises:
            HTTPException: Если отзыв не найден или не принадлежит пользователю
            HTTPException: При ошибках работы с базой данных
        """
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

    async def delete_review(self, review_id: int) -> None:
        """Удаляет отзыв из базы данных.

        Args:
            review_id: ID отзыва для удаления

        Raises:
            HTTPException: При ошибках работы с базой данных
        """
        try:
            await self.db.execute(delete(UserPlaceReview).where(UserPlaceReview.id == review_id))
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении отзыва: {str(e)}")

    async def get_review_by_id(self, review_id: int, user: User) -> UserPlaceReview:
        """Получает отзыв по ID с проверкой владельца.

        Args:
            review_id: ID запрашиваемого отзыва
            user: Пользователь, которому должен принадлежать отзыв

        Returns:
            Найденный объект отзыва

        Raises:
            HTTPException: Если отзыв не найден или не принадлежит пользователю
        """
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