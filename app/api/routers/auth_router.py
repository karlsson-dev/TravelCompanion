from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import UserCreate, UserResponse, TokenResponse, RefreshTokenRequest
from core.config import settings
from domain.repositories import UserRepository
from core.dependencies import get_db
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth", tags=["Аутентификация пользователей"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


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


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """
    Создаёт JWT refresh токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
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

    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Обновление access токена через refresh токен.
    """
    try:
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
