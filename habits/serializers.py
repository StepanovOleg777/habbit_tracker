from rest_framework import serializers
from .models import Habit
from .validators import validate_habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "user")

    def validate(self, data):
        """Валидация данных"""
        habit = Habit(**data) if not self.instance else self.instance

        # Обновляем атрибуты если это частичное обновление
        if self.instance and data:
            for attr, value in data.items():
                setattr(self.instance, attr, value)
            habit = self.instance

        validate_habit(habit)
        return data

    def to_representation(self, instance):
        """Преобразование для вывода"""
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Скрываем связанную привычку для не-владельцев
        if request and request.user != instance.user:
            data.pop("related_habit", None)
            data.pop("reward", None)

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек"""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "periodicity",
            "day_of_week",
            "execution_time",
            "is_pleasant",
            "created_at",
        )
        read_only_fields = fields
