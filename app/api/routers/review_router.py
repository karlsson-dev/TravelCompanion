from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.schemas.review import ReviewCreate, ReviewResponse
from core.dependencies import get_db, get_current_user
from domain.repositories.review_repository import ReviewRepository
from infrastructure.database.models import User

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"],
)


@router.post("/create", response_model=ReviewResponse)
async def create_review(
        review: ReviewCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Создаёт новый отзыв.

    :param review: Данные для создания отзыва.
    :param db: Сессия базы данных для работы с отзывами.
    :param user: обёртка-заглушка для мока OAUTH2.

    :raises HTTPException: Если пользователь не авторизован.

    :return: Созданный отзыв.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    return await repo.create_review(review)


@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
        Получает все отзывы.

        :param db: Сессия базы данных для работы с отзывами.
        :param user: обёртка-заглушка для мока OAUTH2.

        :return: Список всех отзывов.
        """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    return await repo.get_all_reviews()


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
        review_id: int,
        content: str,
        rating: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
        Обновляет существующий отзыв.

        :param review_id: Идентификатор отзыва, который нужно обновить.
        :param content: Новый текст отзыва.
        :param rating: Новый рейтинг.
        :param db: Сессия базы данных для работы с отзывами.
        :param user: обёртка-заглушка для мока OAUTH2.

        :return: Обновлённый отзыв.
        """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    return await repo.update_review(review_id, content, rating)


@router.delete("/{review_id}")
async def delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Удаляет отзыв по его идентификатору.

    :param review_id: Идентификатор отзыва, который нужно удалить.
    :param db: Сессия базы данных для работы с отзывами.
    :param user: обёртка-заглушка для мока OAUTH2.

    :return: Ответ с подтверждением удаления.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    await repo.delete_review(review_id)
    return {"detail": "Отзыв удалён"}
