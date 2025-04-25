from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import UserCreate, UserResponse, TokenResponse
from core.config import settings
from domain.repositories import UserRepository
from core.dependencies import get_db
from jose import jwt
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth", tags=["Аутентификация пользователей"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Создаёт JWT токен доступа с заданным временем истечения.

    :param data: Словарь с данными для кодирования в токен.
    :param expires_delta: Временной интервал до истечения токена. Если не указан, используется значение по умолчанию.
    :return: Закодированный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрирует нового пользователя.

    :param user: Объект с данными нового пользователя.
    :param db: Асинхронная сессия базы данных.
    :return: Данные созданного пользователя.
    :raises HTTPException 400: Если пользователь с таким email или именем уже существует.
    """
    repo = UserRepository(db)
    existing_email = await repo.get_by_email(user.email)
    existing_username = await repo.get_by_username(user.username)

    if existing_email or existing_username:
        raise HTTPException(status_code=400, detail="User already exists")

    created = await repo.create_user(user.username, user.email, user.password)
    return created


@router.post("/login", response_model=TokenResponse)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Аутентифицирует пользователя и возвращает JWT токен.

    :param user: Объект с данными пользователя для входа.
    :param db: Асинхронная сессия базы данных.
    :return: Словарь с токеном доступа и типом токена.
    :raises HTTPException 401: Если имя пользователя или пароль неверны.
    """
    repo = UserRepository(db)
    db_user = await repo.get_by_username(user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя")

    if not repo.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

