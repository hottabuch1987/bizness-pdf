FROM python:3.9-alpine

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Устанавливаем зависимости для PostgreSQL и шрифтов
RUN apk update && \
    apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    fontconfig \
    ttf-dejavu

# Обновляем pip и устанавливаем зависимости из requirements.txt
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем проект и скрипт в контейнер
COPY . .

# Копируем и делаем исполняемым скрипт entrypoint
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Создаем директории для статических и медиа файлов
RUN mkdir -p /usr/src/app/static /usr/src/app/media && \
    chmod -R 755 /usr/src/app/static /usr/src/app/media

# Устанавливаем точку входа
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]
