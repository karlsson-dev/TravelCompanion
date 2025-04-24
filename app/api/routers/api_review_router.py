from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.schemas.review import ReviewCreate, ReviewResponse
from core.dependencies import get_db, get_current_user
from domain.repositories.review_repository import ReviewRepository
from infrastructure.database.models import User

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/api/reviews",
    tags=["Отзывы"],
)

@router.get("/", response_class=HTMLResponse, summary="Главная страница с меню")
async def main_page(request: Request):
    """
    Главная страница с меню.
    """
    return templates.TemplateResponse("main_page.html", {"request": request})

@router.get("/create", response_class=HTMLResponse, summary="Отображает форму для создания отзыва в веб")
async def get_create_review_form(request: Request):
    """
    Отображает форму для создания отзыва.
    :param request: Объект запроса для использования в шаблонах.
    :return: HTML-страница с формой для ввода отзыва.
    """
    return templates.TemplateResponse("create_review.html", {"request": request})

@router.post("/create", summary="Создаёт новый отзыв через форму в веб")
async def post_create_review(
        content: str = Form(...),
        rating: int = Form(...),
        place_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Создаёт новый отзыв через форму.
    :param content: Текст отзыва.
    :param rating: Оценка от 1 до 5.
    :param place_id: ID места, на которое оставляется отзыв.
    :param db: Сессия базы данных для работы с отзывами.
    :param user: Авторизованный пользователь.
    :raises HTTPException: Если пользователь не авторизован.
    :return: Перенаправляет на список всех отзывов.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    review_data = ReviewCreate(content=content, rating=rating, user_id=user.id, place_id=place_id)
    repo = ReviewRepository(db)
    await repo.create_review(review_data)
    return RedirectResponse(url="/api/reviews", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/reviews", response_class=HTMLResponse, summary="Отображает все отзывы в веб")
async def get_reviews(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Отображает все отзывы.
    :param request: Объект запроса для использования в шаблонах.
    :param db: Сессия базы данных для работы с отзывами.
    :return: HTML-страница с отображением всех отзывов.
    """
    repo = ReviewRepository(db)
    reviews = await repo.get_all_reviews()
    return templates.TemplateResponse("reviews.html", {"request": request, "reviews": reviews})

@router.get(
    "/{review_id}/edit",
    response_class=HTMLResponse,
    summary="Отображает форму для редактирования отзыва в веб"
)
async def get_edit_review_form(request: Request, review_id: int, db: AsyncSession = Depends(get_db)):
    """
    Отображает форму для редактирования существующего отзыва.
    :param review_id: Идентификатор отзыва, который нужно обновить.
    :param request: Объект запроса для использования в шаблонах.
    :param db: Сессия базы данных для работы с отзывами.
    :return: HTML-страница с формой для редактирования отзыва.
    """
    repo = ReviewRepository(db)
    review = await repo.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
    return templates.TemplateResponse("edit_review.html", {"request": request, "review": review})

@router.post("/{review_id}/edit", summary="Редактирует существующий отзыв в веб")
async def post_edit_review(
        review_id: int,
        content: str = Form(...),
        rating: int = Form(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Редактирует существующий отзыв.
    :param review_id: Идентификатор отзыва, который нужно обновить.
    :param content: Новый текст отзыва.
    :param rating: Новый рейтинг отзыва (от 1 до 5).
    :param db: Сессия базы данных для работы с отзывами.
    :param user: Авторизованный пользователь.
    :return: Перенаправляет на страницу с отзывами.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    review = await repo.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")

    await repo.update_review(review_id, content, rating)
    return RedirectResponse(url="/api/reviews/reviews", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/{review_id}/delete", response_class=HTMLResponse, summary="Отображает форму для подтверждения удаления отзыва в веб")
async def get_delete_review_form(request: Request, review_id: int, db: AsyncSession = Depends(get_db)):
    """
    Отображает форму для подтверждения удаления отзыва.
    :param review_id: Идентификатор отзыва, который нужно удалить.
    :param request: Объект запроса для использования в шаблонах.
    :param db: Сессия базы данных для работы с отзывами.
    :return: HTML-страница с формой для подтверждения удаления.
    """
    repo = ReviewRepository(db)
    review = await repo.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
    return templates.TemplateResponse("delete_review.html", {"request": request, "review": review})

@router.post("/{review_id}/delete", summary="Удаляет отзыв в веб")
async def post_delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Удаляет отзыв по идентификатору.
    :param review_id: Идентификатор отзыва, который нужно удалить.
    :param db: Сессия базы данных для работы с отзывами.
    :param user: Авторизованный пользователь.
    :return: Перенаправляет на страницу с отзывами.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    repo = ReviewRepository(db)
    await repo.delete_review(review_id)
    return RedirectResponse(url="/api/reviews/reviews", status_code=status.HTTP_303_SEE_OTHER)

# from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
#
# from api.schemas.review import ReviewCreate, ReviewResponse
# from core.dependencies import get_db, get_current_user
# from domain.repositories.review_repository import ReviewRepository
# from infrastructure.database.models import User
#
# templates = Jinja2Templates(directory="templates")
#
# router = APIRouter(
#     prefix="/api/reviews",
#     tags=["Отзывы"],
# )
#
#
# @router.get(
#     "/create",
#     response_class=HTMLResponse,
#     summary="Отображает форму для создания отзыва  в веб"
# )
# async def get_create_review_form(request: Request):
#     """
#     Отображает форму для создания отзыва.
#     :param request: Объект запроса для использования в шаблонах.
#     :return: HTML-страница с формой для ввода отзыва.
#     """
#     return templates.TemplateResponse("create_review.html", {"request": request})
#
#
# @router.post("/create", summary="Создаёт новый отзыв через форму в веб")
# async def post_create_review(
#         content: str = Form(...),
#         rating: int = Form(...),
#         place_id: int = Form(...),
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     """
#     Создаёт новый отзыв через форму.
#     :param content: Текст отзыва.
#     :param rating: Оценка от 1 до 5.
#     :param place_id: ID места, на которое оставляется отзыв.
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#     :raises HTTPException: Если пользователь не авторизован.
#     :return: Перенаправляет на список всех отзывов.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     review_data = ReviewCreate(content=content, rating=rating, user_id=user.id, place_id=place_id)
#     repo = ReviewRepository(db)
#     await repo.create_review(review_data)
#     return RedirectResponse(url="/api/reviews", status_code=status.HTTP_303_SEE_OTHER)
#
#
# @router.get("/", response_class=HTMLResponse, summary="Отображает все отзывы в веб")
# async def get_reviews(request: Request, db: AsyncSession = Depends(get_db)):
#     """
#     Отображает все отзывы.
#     :param request: Объект запроса для использования в шаблонах.
#     :param db: Сессия базы данных для работы с отзывами.
#
#     :return: HTML-страница с отображением всех отзывов.
#     """
#     repo = ReviewRepository(db)
#     reviews = await repo.get_all_reviews()
#     return templates.TemplateResponse("reviews.html", {"request": request, "reviews": reviews})
#
#
# @router.get(
#     "/{review_id}/edit",
#     response_class=HTMLResponse,
#     summary="Отображает форму для редактирования отзыва в веб"
# )
# async def get_edit_review_form(request: Request, review_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Отображает форму для редактирования существующего отзыва.
#     :param request: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param review_id: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param db: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#
#     :return: HTML-<UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     """
#     repo = ReviewRepository(db)
#     review = await repo.get_review_by_id(review_id)
#     if not review:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
#     return templates.TemplateResponse("edit_review.html", {"request": request, "review": review})
#
#
# @router.post("/{review_id}/edit", summary="Редактирует существующий отзыв в веб")
# async def post_edit_review(
#         review_id: int,
#         content: str = Form(...),
#         rating: int = Form(...),
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     """
#     Редактирует существующий отзыв.
#
#     :param review_id: Идентификатор отзыва, который нужно обновить.
#     :param content: Новый текст отзыва.
#     :param rating: Новый рейтинг отзыва (от 1 до 5).
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#
#     :return: Обновленный отзыв в формате HTML.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     review = await repo.get_review_by_id(review_id)
#     if not review:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
#
#     await repo.update_review(review_id, content, rating)
#     return RedirectResponse(url="/api/reviews", status_code=status.HTTP_303_SEE_OTHER)
#
#
# @router.get("/{review_id}/delete", response_class=HTMLResponse,
#             summary="Отображает форму для подтверждения удаления отзыва в веб")
# async def get_delete_review_form(request: Request, review_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Отображает форму для подтверждения удаления отзыва.
#     :param request: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param review_id: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param db: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#
#     :return: HTML-<UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     """
#     repo = ReviewRepository(db)
#     review = await repo.get_review_by_id(review_id)
#     if not review:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
#     return templates.TemplateResponse("delete_review.html", {"request": request, "review": review})
#
#
# @router.post("/{review_id}/delete", summary="Удаляет отзыв в веб")
# async def post_delete_review(
#         review_id: int,
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     """
#     Удаляет отзыв по идентификатору.
#     :param review_id: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param db: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     :param user: <UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#
#     :return: HTML-<UNK> <UNK> <UNK> <UNK> <UNK> <UNK>.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     await repo.delete_review(review_id)
#     return RedirectResponse(url="/api/reviews", status_code=status.HTTP_303_SEE_OTHER)
#
#
# @router.post("/create", response_model=ReviewResponse, summary="Создаёт новый отзыв через API")
# async def create_review(
#         review: ReviewCreate,
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     """
#     Создаёт новый отзыв через API.
#     :param review: Данные для создания отзыва.
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#
#     :raises HTTPException: Если пользователь не авторизован.
#
#     :return: Созданный отзыв.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     return await repo.create_review(review)
#
#
# @router.get("/", response_model=List[ReviewResponse], summary="Получает все отзывы через API")
# async def list_reviews(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
#     """
#     Получает все отзывы через API.
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#
#     :raises HTTPException: Если пользователь не авторизован.
#
#     :return: Список всех отзывов.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     return await repo.get_all_reviews()
#
#
# @router.put(
#     "/{review_id}",
#     response_model=ReviewResponse,
#     summary="Обновляет существующий отзыв через API"
# )
# async def update_review(
#         review_id: int,
#         content: str,
#         rating: int,
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user),
# ):
#     """
#     Обновляет существующий отзыв.
#     :param review_id: Идентификатор отзыва, который нужно обновить.
#     :param content: Новый текст отзыва.
#     :param rating: Новый рейтинг.
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#
#     :raises HTTPException: Если пользователь не авторизован.
#
#     :return: Обновлённый отзыв.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     return await repo.update_review(review_id, content, rating)
#
#
# @router.delete("/{review_id}", summary="Удаляет отзыв через API")
# async def delete_review(
#         review_id: int,
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_user)
# ):
#     """
#     Удаляет отзыв по его идентификатору.
#     :param review_id: Идентификатор отзыва, который нужно удалить.
#     :param db: Сессия базы данных для работы с отзывами.
#     :param user: Авторизованный пользователь.
#
#     :raises HTTPException: Если пользователь не авторизован.
#
#     :return: Ответ с подтверждением удаления.
#     """
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#
#     repo = ReviewRepository(db)
#     await repo.delete_review(review_id)
#     return {"detail": "Отзыв удалён"}
