from celery import shared_task
from django.utils import timezone
from datetime import datetime
from .models import Habit
from .telegram_bot import TelegramBot
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminders():
    """
    Отправка напоминаний о привычках
    Запускается каждую минуту
    """
    try:
        now = timezone.localtime()
        current_time = now.time().replace(second=0, microsecond=0)
        current_weekday = now.strftime("%A").lower()

        # Маппинг английских названий дней на русские
        day_mapping = {
            "monday": "понедельник",
            "tuesday": "вторник",
            "wednesday": "среда",
            "thursday": "четверг",
            "friday": "пятница",
            "saturday": "суббота",
            "sunday": "воскресенье",
        }

        current_day_russian = day_mapping.get(current_weekday, "")

        # Получаем привычки, которые нужно выполнить в это время
        habits = Habit.objects.filter(
            time__hour=current_time.hour,
            time__minute=current_time.minute,
        ).select_related("user")

        telegram_bot = TelegramBot()
        reminders_sent = 0

        for habit in habits:
            # Проверяем, нужно ли отправлять напоминание
            should_send = False

            if habit.periodicity == "daily":
                should_send = True
            elif habit.periodicity == "weekly":
                if habit.day_of_week == current_day_russian:
                    should_send = True

            if should_send and habit.user.telegram_chat_id:
                success = telegram_bot.send_habit_reminder(habit.user, habit)
                if success:
                    reminders_sent += 1
                    logger.info(
                        f"Напоминание отправлено для привычки {habit.id} пользователю {habit.user.username}"
                    )

        return f"Отправлено {reminders_sent} напоминаний в {current_time}"

    except Exception as e:
        logger.error(f"Ошибка в задаче send_habit_reminders: {e}")
        return f"Ошибка: {e}"


@shared_task
def test_task():
    """Тестовая задача для проверки работы Celery"""
    return "Celery работает!"
