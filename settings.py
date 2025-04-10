from pathlib import Path
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACE_SERVICE_PORT=8000
HOTEL_SERVICE_PORT=8001

class Settings(BaseSettings):
    # place_service
    PLACE_DB_HOST: str
    PLACE_DB_PORT: int
    PLACE_DB_NAME: str
    PLACE_DB_USER: str
    PLACE_DB_PASSWORD: str

    # hotel_service
    HOTEL_DB_HOST: str
    HOTEL_DB_PORT: int
    HOTEL_DB_NAME: str
    HOTEL_DB_USER: str
    HOTEL_DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )

    @field_validator("PLACE_DB_PORT", "HOTEL_DB_PORT", mode="before")
    @classmethod
    def validate_port(cls, port: int) -> int:
        if not 1 <= int(port) <= 65535:
            raise ValueError("DB_PORT должен быть между 1 и 65535")
        return int(port)

    @field_validator("PLACE_DB_PASSWORD", "HOTEL_DB_PASSWORD", mode="before")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("DB_PASSWORD не может быть пустым")
        return password

    @field_validator("PLACE_DB_HOST", "HOTEL_DB_HOST", mode="before")
    @classmethod
    def validate_host(cls, host: str) -> str:
        host = host.strip()
        if not host:
            raise ValueError("DB_HOST не может быть пустым")
        if host not in ("localhost", "127.0.0.1") and "." not in host:
            raise ValueError("DB_HOST должно быть действительным именем хоста или IP")
        return host


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Неверная конфигурация .env: {e}")


def get_place_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.PLACE_DB_USER}:{settings.PLACE_DB_PASSWORD}@"
        f"{settings.PLACE_DB_HOST}:{settings.PLACE_DB_PORT}/{settings.PLACE_DB_NAME}"
    )


def get_hotel_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.HOTEL_DB_USER}:{settings.HOTEL_DB_PASSWORD}@"
        f"{settings.HOTEL_DB_HOST}:{settings.HOTEL_DB_PORT}/{settings.HOTEL_DB_NAME}"
    )
