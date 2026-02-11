from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для пользователей"""

    list_display = (
        "id",
        "username",
        "email",
        "telegram_chat_id",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("username", "email", "telegram_chat_id")

    fieldsets = UserAdmin.fieldsets + (("Telegram", {"fields": ("telegram_chat_id",)}),)

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Telegram", {"fields": ("telegram_chat_id",)}),
    )
