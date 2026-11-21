# Skystore — каталог товаров на Django

Учебный проект: каталог товаров и блог. PostgreSQL, админка, фикстуры, контроллеры на классах (CBV), формы с проверками.

## Быстрый старт (Windows)

1. Создайте базу в PostgreSQL (через pgAdmin или psql):

   ```sql
   CREATE DATABASE skystore_users_db;
   ```

2. Скопируйте `.env.sample` в `.env` и впишите свой пароль от PostgreSQL в `POSTGRES_PASSWORD`.
3. Запустите `setup.bat` двойным щелчком или из терминала. Скрипт установит зависимости, создаст таблицы, создаст группы, загрузит тестовые товары, попросит email и пароль администратора и запустит сервер.
4. Откройте http://127.0.0.1:8000/

Суперпользователь для админки (http://127.0.0.1:8000/admin/):

```bash
poetry run python manage.py createsuperuser
```

## Запуск вручную

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py add_products
poetry run python manage.py runserver
```

Все команды пишутся через `poetry run`: так они выполняются в виртуальном окружении проекта, где установлен Django.

## Страницы

| Адрес | Что там |
|---|---|
| `/` | список товаров |
| `/products/create/` | новый товар |
| `/products/<pk>/` | страница товара |
| `/products/<pk>/update/` | редактирование товара |
| `/products/<pk>/delete/` | удаление товара |
| `/products/<pk>/unpublish/` | снять с публикации (модератор, только POST) |
| `/users/register/` | регистрация (после неё приходит приветственное письмо) |
| `/users/login/` | вход по email и паролю |
| `/users/profile/` | редактирование профиля (только для вошедших) |
| `/contacts/` | контакты и форма обратной связи |
| `/blogs/` | список опубликованных статей |
| `/blogs/create/` | новая статья |
| `/blogs/<pk>/` | статья (при каждом открытии растёт счётчик просмотров) |
| `/blogs/<pk>/update/` | редактирование статьи, после сохранения открывается статья |
| `/blogs/<pk>/delete/` | удаление статьи |

## Пользователи

Приложение `users`: модель `User` (наследник `AbstractUser`), вход по email (`USERNAME_FIELD = "email"`), дополнительные поля — аватар, телефон, страна.

Без входа доступен только список товаров. Просмотр, создание, изменение и удаление товара закрыты декоратором `login_required` (`catalog/urls.py`) — гостя перенаправит на страницу входа.

Письма по умолчанию печатаются в терминал, где запущен `runserver`. Чтобы отправлять настоящие письма, заполните SMTP-настройки в `.env` (пример в `.env.sample`).

## Роли и права

Группы создаёт команда (её же запускает `setup.bat`):

```bash
poetry run python manage.py create_groups
# сразу добавить пользователей в группы:
poetry run python manage.py create_groups --moderator moder@example.com --content-manager editor@example.com
```

| Кто | Что может |
|---|---|
| Гость | видеть список опубликованных товаров и блог |
| Пользователь | создавать товары (он становится владельцем), изменять и удалять только свои |
| «Модератор продуктов» | права `can_unpublish_product` и `delete_product`: снимать любой товар с публикации и удалять любой товар |
| «Контент-менеджер» | создавать, изменять и удалять статьи блога |

Новый товар по умолчанию не опубликован (`is_published = False`) и виден только владельцу и модераторам, пока владелец не отметит «Опубликован». Кнопки «Редактировать», «Удалить» и «Снять с публикации» показываются только тем, кому они доступны; прямой переход по адресу без прав вернёт страницу «Нет доступа».

## Проверки в форме товара

`ProductForm` в `catalog/forms.py`:

- в названии и описании нельзя использовать слова из списка `FORBIDDEN_WORDS` (регистр не важен);
- цена не может быть отрицательной (`clean_price`);
- изображение — только JPEG или PNG, не больше 5 МБ (`clean_image`).

Стили Bootstrap всем формам добавляет `StyleFormMixin` в методе `__init__`.

## Тестовые данные

`add_products` удаляет все категории и товары и загружает фикстуры из `catalog/fixtures/`. Загрузить их вручную:

```bash
poetry run python manage.py loaddata category.json
poetry run python manage.py loaddata product.json
```

Выгрузить данные в фикстуры (`-Xutf8` нужен на Windows, чтобы сохранилась кириллица):

```bash
poetry run python -Xutf8 manage.py dumpdata catalog.Category --indent 4 -o catalog/fixtures/category.json
poetry run python -Xutf8 manage.py dumpdata catalog.Product --indent 4 -o catalog/fixtures/product.json
```

## Структура

- `config/` — настройки проекта
- `catalog/` — товары, категории, контакты: модели, формы, контроллеры, шаблоны, фикстуры, команда `add_products`
- `catalog/templates/catalog/base.html` — базовый шаблон; `includes/` — подшаблоны (меню, поля формы, изображение товара)
- `blog/` — приложение блога
- `users/` — пользователи: модель, регистрация, вход, профиль
- `screenshots/` — скриншоты работы в Django shell
