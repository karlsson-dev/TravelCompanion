from pathlib import Path
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer

SERVICE_PORT = 8000

PORT_MIN = 1
PORT_MAX = 65535

ALGORITHM = "HS256"


class Settings(BaseSettings):
    # place_service
    PLACE_DB_HOST: str
    PLACE_DB_PORT: int
    PLACE_DB_NAME: str
    PLACE_DB_USER: str
    PLACE_DB_PASSWORD: str

    # hotel_service
    REDIS_URL: str
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    OPENTRIPMAP_API_KEY: str
    OPENTRIPMAP_URL: str

    # auth
    USE_FAKE_AUTH: bool = False
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    NOMINATIM_URL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        extra="ignore",
    )

    @field_validator("PLACE_DB_PORT", mode="before")
    @classmethod
    def validate_port(cls, port: int) -> int:
        if not PORT_MIN <= int(port) <= PORT_MAX:
            raise ValueError(f"DB_PORT должен быть между {PORT_MIN} и {PORT_MAX}")

        return int(port)

    @field_validator("PLACE_DB_PASSWORD", mode="before")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("DB_PASSWORD не может быть пустым")
        return password

    @field_validator("PLACE_DB_HOST", mode="before")
    @classmethod
    def validate_host(cls, host: str) -> str:
        host = host.strip()
        if not host:
            raise ValueError("DB_HOST не может быть пустым")
        if host not in ("localhost", "127.0.0.1") and "." not in host:
            raise ValueError("DB_HOST должно быть действительным именем хоста или IP")
        return host


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Неверная конфигурация .env: {e}")


def get_place_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.PLACE_DB_USER}:{settings.PLACE_DB_PASSWORD}@"
        f"{settings.PLACE_DB_HOST}:{settings.PLACE_DB_PORT}/{settings.PLACE_DB_NAME}")
