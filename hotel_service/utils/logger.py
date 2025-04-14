from loguru import logger
import sys
import os


def setup_logger():
    log_path = "logs"
    os.makedirs(log_path, exist_ok=True)

    logger.remove()  # Убираем стандартный вывод

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        enqueue=True,
    )

    logger.add(
        f"{log_path}/app.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        enqueue=True,
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    )
