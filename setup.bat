@echo off
chcp 65001 > nul
rem Первый запуск проекта на Windows: зависимости, таблицы в базе, тестовые данные, сервер.
rem Перед запуском: создайте базу в PostgreSQL и файл .env (см. README.md).

if not exist .env (
    echo Нет файла .env. Скопируйте .env.sample в .env и впишите пароль от PostgreSQL.
    pause
    exit /b 1
)

echo === Установка зависимостей ===
poetry install || goto :error

echo === Создание таблиц в базе ===
poetry run python manage.py migrate || goto :error

echo === Создание групп пользователей ===
poetry run python manage.py create_groups || goto :error

echo === Загрузка тестовых товаров ===
poetry run python manage.py add_products || goto :error

echo === Создание администратора (введите email и пароль) ===
poetry run python manage.py createsuperuser || goto :error

echo === Запуск сервера: http://127.0.0.1:8000/ ===
poetry run python manage.py runserver
exit /b 0

:error
echo.
echo Что-то пошло не так. Скопируйте текст ошибки выше.
pause
exit /b 1
