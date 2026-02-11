from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "place",
        "time",
        "periodicity",
        "is_public",
        "is_pleasant",
    )
    list_filter = ("is_public", "is_pleasant", "periodicity", "user")
    search_fields = ("action", "place", "user__username")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "action", "place", "time", "execution_time")},
        ),
        ("Периодичность", {"fields": ("periodicity", "day_of_week")}),
        (
            "Вознаграждение и связи",
            {"fields": ("reward", "related_habit", "is_pleasant")},
        ),
        ("Дополнительно", {"fields": ("is_public", "created_at", "updated_at")}),
    )
