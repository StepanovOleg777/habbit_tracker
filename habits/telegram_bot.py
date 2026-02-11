import logging
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}/"

    def send_message(self, chat_id: str, text: str) -> bool:
        """
        Отправка сообщения через Telegram Bot API

        Args:
            chat_id: ID чата
            text: Текст сообщения

        Returns:
            bool: Успешно ли отправлено
        """
        if not self.token:
            logger.warning("Токен Telegram бота не настроен")
            return False

        try:
            url = f"{self.api_url}sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отправке в Telegram: {e}")
            return False

    def send_habit_reminder(self, user, habit):
        """
        Отправка напоминания о привычке

        Args:
            user: Пользователь
            habit: Привычка
        """
        if not user.telegram_chat_id:
            logger.warning(f"У пользователя {user.username} не указан telegram_chat_id")
            return False

        message = (
            f"⏰ <b>Напоминание о привычке!</b>\n\n"
            f"📝 <b>Действие:</b> {habit.action}\n"
            f"📍 <b>Место:</b> {habit.place}\n"
            f"⏱️ <b>Время на выполнение:</b> {habit.execution_time} секунд\n"
            f"📅 <b>Периодичность:</b> {habit.get_periodicity_display()}\n"
        )

        if habit.reward:
            message += f"🎁 <b>Вознаграждение:</b> {habit.reward}\n"

        message += f"\nУдачи! 💪"

        return self.send_message(user.telegram_chat_id, message)
