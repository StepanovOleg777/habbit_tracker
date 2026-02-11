import os
from celery import Celery

# Установка переменной окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра Celery
app = Celery("config")

# Загрузка настроек из настроек Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
