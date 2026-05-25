FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# рабочая папка внутри контейнера
WORKDIR /app

# устанавливаем системные зависимости (для postgres)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# копируем requirements
COPY requirements.txt /app/

# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь проект
COPY . /app/

# открываем порт
EXPOSE 8000

# команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]