FROM python:3.9.6-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем всё приложение
COPY ./app ./app

# Переменные окружения
ENV PYTHONPATH=/app/app

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
