import asyncio
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import logging.config
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.logger import logger
from core.config import get_place_db_url

DATABASE_URL = get_place_db_url()

# Настройка Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Отключаем стандартное логирование Alembic (если используем loguru)
if config.config_file_name is not None:
    import logging

    logging.config.fileConfig(config.config_file_name, disable_existing_loggers=False)
    logger.info("Alembic logging configured")

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import User, Place,Rating, Review, UserTrip, UserPlaceHistory, UserVisit

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
