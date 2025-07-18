# Интернет-магазин

Платформа для электронной коммерции на Django, включающая аутентификацию пользователей, просмотр товаров, оформление заказов, управление профилями, панель администратора, API и интеграцию с Telegram-ботом.

## Описание проекта

Разработала платформу для электронной коммерции на Django, работая над аутентификацией пользователей, просмотром товаров и управлением заказами.

**В мои обязанности входило:**
- **Реализация системы аутентификации с использованием Django Auth**
- **Создание функционала просмотра товаров и оформления заказов, управление профилями пользователей и историей заказов**
- **Разработка панели администратора для управления товарами, заказами и пользователями**
- **Создание API CRUD с Django REST Framework**
- **Интеграция аутентификации JWT, email-уведомлений и Telegram-бота для обновления статуса заказов**

## Технологии

- **Python 3.10+**
- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Docker**
- **JWT (JSON Web Tokens)**
- **Email-уведомления**
- **Telegram Bot API**
- **HTML, CSS**

## Быстрый старт

### 1. Клонируйте репозиторий

`git clone https://github.com/antasia03/store_project`
`cd store_project`


### 2. Настройка окружения

Создайте файл `.env` в корне проекта и заполните его по примеру.  
Пример содержимого `.env`:

POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=*
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
TELEGRAM_BOT_TOKEN=your_telegram_bot_token


### 3. Запуск через Docker

`docker-compose up --build`


После запуска проект будет доступен по адресу:  
http://localhost:8000/



### 4. Создание суперпользователя

`docker-compose exec web python manage.py createsuperuser`


## Доступ к панели администратора

Адрес:  
http://localhost:8000/admin/


Войдите под логином и паролем суперпользователя.

## API

API доступно по адресу:  
http://localhost:8000/api/

**Функционал:**
- **Аутентификация через JWT**
- **CRUD для товаров, заказов, пользователей**
- **Просмотр истории заказов**

## Email-уведомления

Для локальной разработки email-уведомления выводятся в консоль.  
Для реальной отправки писем настройте SMTP в `.env`:

EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = your_email@gmail.com
EMAIL_HOST_PASSWORD = your_password


## Telegram-бот

Telegram-бот уведомляет пользователей об изменении статуса заказа.  
Для работы бота укажите токен в `.env`:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
