from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Habit(models.Model):
    PERIOD_CHOICES = [
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
    ]

    DAY_CHOICES = [
        ("monday", "Понедельник"),
        ("tuesday", "Вторник"),
        ("wednesday", "Среда"),
        ("thursday", "Четверг"),
        ("friday", "Пятница"),
        ("saturday", "Суббота"),
        ("sunday", "Воскресенье"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )

    place = models.CharField(max_length=255, verbose_name="Место выполнения")

    time = models.TimeField(verbose_name="Время выполнения")

    action = models.CharField(max_length=255, verbose_name="Действие")

    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )

    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_habits",
        verbose_name="Связанная привычка",
        limit_choices_to={"is_pleasant": True},
    )

    periodicity = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default="daily",
        verbose_name="Периодичность",
    )

    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
        null=True,
        blank=True,
        verbose_name="День недели",
    )

    reward = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Вознаграждение"
    )

    execution_time = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)", help_text="Максимум 120 секунд"
    )

    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]
        db_table = "habits"

    def __str__(self):
        return f"{self.user.username}: {self.action} в {self.time}"

    def clean(self):
        from .validators import validate_habit

        validate_habit(self)

        # Дополнительная валидация
        if self.periodicity == "weekly" and not self.day_of_week:
            raise ValidationError(
                "Для еженедельной привычки необходимо указать день недели."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
