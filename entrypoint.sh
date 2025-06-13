#!/bin/sh
set -e  # Останавливаем выполнение при ошибке

if [ "$DATABASE" = "postgres" ]; then
    echo "База еще не запущена..."
    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
        sleep 0.1
    done
    echo "DB did run."
fi

# Удаляем старые данные (если нужно)
# python manage.py flush --no-input

# Выполняем миграции и собираем статические файлы
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

# Выполняем переданные контейнеру команды
exec "$@"
