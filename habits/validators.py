from django.core.exceptions import ValidationError
from datetime import time


def validate_habit(habit):
    """
    Валидатор привычек согласно ТЗ:
    1. Нельзя одновременно выбирать связанную привычку и вознаграждение
    2. Время выполнения не больше 120 секунд
    3. Связанная привычка должна быть приятной
    4. У приятной привычки не может быть вознаграждения или связанной привычки
    5. Нельзя выполнять привычку реже 1 раза в 7 дней
    """

    # Проверка 1: Нельзя одновременно выбирать связанную привычку и вознаграждение
    if habit.related_habit and habit.reward:
        raise ValidationError(
            "Нельзя одновременно указывать связанную привычку и вознаграждение. "
            "Выберите что-то одно."
        )

    # Проверка 2: Время выполнения не больше 120 секунд
    if habit.execution_time > 120:
        raise ValidationError(
            f"Время выполнения не должно превышать 120 секунд. "
            f"Вы указали {habit.execution_time} секунд."
        )

    # Проверка 3: Связанная привычка должна быть приятной
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError(
            "Связанная привычка должна быть приятной "
            "(иметь признак 'Приятная привычка')."
        )

    # Проверка 4: У приятной привычки не может быть вознаграждения или связанной привычки
    if habit.is_pleasant:
        if habit.reward:
            raise ValidationError("У приятной привычки не может быть вознаграждения.")
        if habit.related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )

    # Проверка 5: Нельзя выполнять привычку реже 1 раза в 7 дней
    if habit.periodicity not in ["daily", "weekly"] and not habit.day_of_week:
        raise ValidationError(
            "Привычка должна выполняться не реже 1 раза в 7 дней. "
            "Выберите 'Ежедневно' или укажите день недели."
        )
