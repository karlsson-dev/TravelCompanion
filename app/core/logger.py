import sys
from loguru import logger

# Настройка логирования через loguru для удобства
def setup_logger():
    # Убираем стандартный обработчик loguru
    logger.remove()

    # Добавляем вывод в терминал
    logger.add(sys.stdout, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

    # Логируем в файл
    logger.add("app.log", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", rotation="1 MB")

# Вызов настройки логирования
setup_logger()
