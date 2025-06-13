FROM python:3.9-alpine

WORKDIR /usr/src/app

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости для Postgre

RUN apk update && \
    apk add --no-cache \
    weasyprint \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    fontconfig \
    ttf-dejavu \
    glib-dev \
    gobject-introspection-dev


RUN apk add --no-cache \
    cairo-dev \
    pango-dev \
    libffi-dev
# устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Копируем проект и скрипт в контейнер
COPY . .
COPY entrypoint.sh /usr/src/app/entrypoint.sh

# Делаем скрипт исполняемым
RUN chmod +x /usr/src/app/entrypoint.sh

RUN mkdir -p /usr/src/app/static /usr/src/app/media && \
     chmod -R 755 /usr/src/app/static /usr/src/app/media


# Устанавливаем точку входа
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]

