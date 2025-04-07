from pathlib import Path
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="ignore",
    )

    @field_validator("DB_PORT")
    def validate_port(cls, port: int) -> int:
        if not 1 <= port <= 65535:
            raise ValueError("DB_PORT должен быть между 1 и 65535")
        return port

    @field_validator("DB_PASSWORD")
    def validate_password(cls, pwd: str) -> str:
        if not pwd.strip():
            raise ValueError("DB_PASSWORD не может быть пустым")
        return pwd

    @field_validator("DB_HOST")
    def validate_host(cls, host: str) -> str:
        if not host.strip():
            raise ValueError("DB_HOST не может быть пустым")
        if host not in ("localhost", "127.0.0.1") and "." not in host:
            raise ValueError("DB_HOST должно быть действительным именем хоста или IP")
        return host


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Не верная конфигурация .env: {e}")


def get_db():
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
