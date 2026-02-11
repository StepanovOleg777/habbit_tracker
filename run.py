#!/usr/bin/env python
import os
import sys
import subprocess
import platform
from dotenv import load_dotenv

load_dotenv()


def print_header(text):
    """Вывод заголовка"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def run_command(command, description, wait=False):
    """Запуск команды"""
    print_header(description)
    print(f"Команда: {command}\n")

    try:
        if wait:
            subprocess.run(command, shell=True)
        else:
            subprocess.Popen(command, shell=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def check_postgresql():
    """Проверка PostgreSQL"""
    print_header("Проверка PostgreSQL")

    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        password = os.getenv("DB_PASSWORD", "postgres")

        # Подключаемся к postgres
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password=password,
            host="localhost",
            port="5432",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверяем наличие БД
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'habbit_tracker'")
        exists = cursor.fetchone()

        if not exists:
            print("❌ База данных habbit_tracker не найдена")
            create = input("Создать базу данных habbit_tracker? (y/n): ")
            if create.lower() == "y":
                cursor.execute("CREATE DATABASE habbit_tracker")
                print("✅ База данных habbit_tracker создана")
            else:
                print("⚠️ База данных не создана, проект не сможет работать")
                return False
        else:
            print("✅ База данных habbit_tracker существует")

        cursor.close()
        conn.close()

        # Проверяем подключение
        conn = psycopg2.connect(
            database="habbit_tracker",
            user="postgres",
            password=password,
            host="localhost",
            port="5432",
        )
        conn.close()
        print("✅ Подключение к PostgreSQL успешно")
        return True

    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        print("\nПроверьте:")
        print("1. Запущен ли pgAdmin 4")
        print("2. Правильный ли пароль в .env файле (DB_PASSWORD)")
        print("3. Что сервер PostgreSQL запущен")
        return False


def check_redis():
    """Проверка Redis"""
    print_header("Проверка Redis")

    try:
        import redis

        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
        )
        r.ping()
        print("✅ Redis запущен")
        return True
    except:
        print("⚠️ Redis не запущен или не установлен")
        print("   Celery задачи работать не будут")
        print("   Для работы напоминаний установите Redis/Memurai")
        return False


def create_superuser_interactive():
    """Интерактивное создание суперпользователя"""
    print_header("Создание суперпользователя")
    print("Создайте администратора для доступа к /admin\n")

    try:
        # Запускаем createsuperuser в интерактивном режиме
        subprocess.run("python manage.py createsuperuser", shell=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании суперпользователя: {e}")
        return False


def main():
    """Главная функция"""

    if len(sys.argv) < 2:
        print_header("Управление проектом Habit Tracker")
        print("Использование: python run.py [команда]\n")
        print("Доступные команды:")
        print("  setup          - Первоначальная настройка проекта")
        print("  server         - Запуск Django сервера")
        print("  celery         - Запуск Celery worker")
        print("  beat           - Запуск Celery beat")
        print("  migrate        - Применение миграций")
        print("  makemigrations - Создание миграций")
        print("  superuser      - Создание суперпользователя (администратора)")
        print("  test           - Запуск тестов")
        print("  coverage       - Проверка покрытия тестами")
        print("  flake8         - Проверка кода")
        print("  shell          - Django shell")
        print("  check_db       - Проверка PostgreSQL")
        print("  check_redis    - Проверка Redis")
        print("\nПримеры:")
        print("  python run.py setup")
        print("  python run.py server")
        print("  python run.py superuser")
        return

    command = sys.argv[1]

    if command == "setup":
        print_header("Первоначальная настройка проекта")

        # Проверка PostgreSQL
        check_postgresql()

        # Миграции
        run_command("python manage.py makemigrations users", "Создание миграций users")
        run_command(
            "python manage.py makemigrations habits", "Создание миграций habits"
        )
        run_command("python manage.py migrate", "Применение миграций")

        # Сбор статики
        run_command(
            "python manage.py collectstatic --noinput", "Сбор статических файлов"
        )

        print_header("Настройка завершена!")
        print("Далее выполните:")
        print("1. python run.py superuser - Создать администратора")
        print("2. python run.py server - Запустить сервер")
        print("3. Откройте http://127.0.0.1:8000/admin/ для управления")

    elif command == "server":
        run_command("python manage.py runserver", "Запуск Django сервера", wait=True)

    elif command == "celery":
        run_command(
            "celery -A config worker --loglevel=info -P solo",
            "Запуск Celery worker",
            wait=True,
        )

    elif command == "beat":
        run_command(
            "celery -A config beat --loglevel=info", "Запуск Celery beat", wait=True
        )

    elif command == "superuser":
        create_superuser_interactive()

    elif command == "migrate":
        run_command("python manage.py migrate", "Применение миграций")

    elif command == "makemigrations":
        app = sys.argv[2] if len(sys.argv) > 2 else ""
        run_command(f"python manage.py makemigrations {app}", "Создание миграций")

    elif command == "test":
        run_command("python manage.py test", "Запуск тестов")

    elif command == "coverage":
        run_command("coverage run manage.py test", "Запуск тестов с покрытием")
        run_command("coverage report", "Отчет о покрытии")
        run_command("coverage html", "HTML отчет о покрытии")
        print("\n✅ HTML отчет создан: открыть htmlcov/index.html")

    elif command == "flake8":
        run_command(
            "flake8 --exclude=migrations --max-line-length=120", "Проверка кода Flake8"
        )

    elif command == "shell":
        run_command("python manage.py shell_plus", "Django shell", wait=True)

    elif command == "check_db":
        check_postgresql()

    elif command == "check_redis":
        check_redis()

    elif command == "all":
        print_header("Запуск всех компонентов")
        print("⚠️  Откройте 3 отдельных терминала и выполните:")
        print("\nТерминал 1: python run.py server")
        print("Терминал 2: python run.py celery")
        print("Терминал 3: python run.py beat")

    else:
        print(f"❌ Неизвестная команда: {command}")


if __name__ == "__main__":
    main()
