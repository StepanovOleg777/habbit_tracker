from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_chat_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ID чата Telegram"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        db_table = "users"

    def __str__(self):
        return self.username
