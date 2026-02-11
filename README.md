# Habit Tracker API
Бэкенд-часть SPA веб-приложения для трекинга полезных привычек.
Проект реализован на основе книги Джеймса Клира «Атомные привычки».

## 🚀 Функциональность
✅ Регистрация и авторизация пользователей (JWT)

✅ CRUD для привычек

✅ Публичные и приватные привычки

✅ Пагинация (5 привычек на страницу)

✅ Валидация данных по ТЗ

✅ Интеграция с Telegram (напоминания)

✅ Celery + Redis (отложенные задачи)

✅ Swagger / ReDoc документация

✅ CORS

✅ Покрытие тестами >80%

## 🛠 Стек технологий
Python 3.13

Django 4.2.11

Django REST Framework

PostgreSQL

Redis

Celery

JWT (djangorestframework-simplejwt)

python-telegram-bot

drf-yasg (Swagger)

## 📦 Установка и запуск
1. Клонировать репозиторий
bash
git clone https://github.com/ваш-username/habbit_tracker.git
cd habbit_tracker
2. Создать и активировать виртуальное окружение
bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
3. Установить зависимости
bash
pip install -r requirements.txt
4. Настройка переменных окружения
Скопируйте .env.example в .env и отредактируйте:

bash
cp .env.example .env
Обязательно укажите:

DB_PASSWORD — пароль от PostgreSQL

TELEGRAM_BOT_TOKEN — токен бота от @BotFather

5. Создать базу данных
Через pgAdmin 4 или командную строку:

sql
CREATE DATABASE habbit_tracker;
6. Применить миграции
bash
python manage.py migrate
7. Создать суперпользователя (для админки)
bash
python manage.py createsuperuser
8. Запустить сервер
bash
python manage.py runserver
9. Запустить Celery (в отдельных терминалах)
bash
### Worker
celery -A config worker --loglevel=info -P solo

### Beat (для периодических задач)
celery -A config beat --loglevel=info
📚 Документация API
После запуска сервера доступно:

Swagger UI: http://127.0.0.1:8000/swagger/

ReDoc: http://127.0.0.1:8000/redoc/

## 🤖 Telegram бот
Бот не отвечает на команды — он только отправляет уведомления.

### Как настроить:

Напишите @BotFather в Telegram

Создайте нового бота (/newbot)

Скопируйте токен в .env: TELEGRAM_BOT_TOKEN=...

Напишите боту любое сообщение (активация)

В админке укажите telegram_chat_id пользователя

Уведомления приходят автоматически в указанное время привычки.

## 🧪 Тестирование
bash
### Запуск тестов
python manage.py test

### Проверка покрытия
coverage run manage.py test
coverage report
coverage html  # открыть htmlcov/index.html

### Проверка стиля кода
flake8 --exclude=migrations --max-line-length=120
## 📁 Структура проекта

habbit_tracker/
├── config/              # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── users/              # Пользователи
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── habits/             # Привычки
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── validators.py
│   ├── permissions.py
│   ├── pagination.py
│   ├── tasks.py        # Celery задачи
│   └── telegram_bot.py
├── .env.example        # Шаблон переменных окружения
├── requirements.txt    # Зависимости
└── manage.py
## 🔒 Права доступа
Только владелец может редактировать/удалять свои привычки

Публичные привычки доступны всем авторизованным пользователям (только чтение)

Приватные привычки видит только владелец

## ✅ Валидация
Нельзя одновременно указать reward и related_habit

Время выполнения ≤ 120 секунд

Связанная привычка должна быть приятной (is_pleasant=True)

У приятной привычки нет вознаграждения или связанной привычки

Периодичность — не реже 1 раза в 7 дней

## 📄 Лицензия
Проект выполнен в рамках учебного курсового проекта.

# Автор: StepanovOleg777
GitHub: https://github.com/StepanovOleg777/habbit_tracker/tree/feature/work_1