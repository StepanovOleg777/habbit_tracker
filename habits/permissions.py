from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на чтение для всех, на изменение только для владельца.
    Для публичных привычек - чтение для всех, изменение только для владельца.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            # Для публичных привычек разрешаем чтение всем
            if obj.is_public:
                return True
            # Для приватных привычек - только владельцу
            return obj.user == request.user

        # Запись (POST, PUT, PATCH, DELETE) - только владельцу
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """Только владелец имеет доступ"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
