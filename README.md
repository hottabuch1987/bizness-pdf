![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Проект позвозволяет загружать файлы формата csv в базу данных, редактировать и удалять выбранные категории.
## Переобразовывать в pdf выбранные категории с двумя вариантами шаблонов.

## Документация по развертыванию проекта c помощью docker 

1. Клонируйте репозиторий


2. Соберите и запустите контейнеры:
    ```
    docker-compose up --build
    ```
## Документация по развертыванию проекта локально

1. Клонируйте репозиторий

2. Создайте и активируйте виртальное окружение
    ```
    python3 -m venv venv
    ```
    ```
    source venv/bin/activate
    ```
3. Установите зависимости
    ```
    pip install -r requirements.txt
    ```
4. Мигрируйте базу и запустите сервевер
    ```
    python manage.py migrate
    ```
    ```
    python manage.py runserver
    ```
