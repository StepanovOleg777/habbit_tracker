from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer
from .permissions import IsOwnerOrReadOnly
from .pagination import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "periodicity", "is_public"]

    def get_queryset(self):
        """Получение списка привычек"""
        # Для генерации схемы Swagger возвращаем пустой queryset
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()

        user = self.request.user

        # Для анонимных пользователей возвращаем пустой queryset
        if user.is_anonymous:
            return Habit.objects.none()

        # Для списка привычек пользователя
        if self.action == "list":
            return Habit.objects.filter(user=user)

        # Для остальных действий
        return Habit.objects.filter(Q(user=user) | Q(is_public=True))

    def get_permissions(self):
        """Получение прав доступа для разных действий"""
        if self.action in ["public", "list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def public(self, request):
        """Список публичных привычек (доступно всем авторизованным)"""
        habits = Habit.objects.filter(is_public=True)

        # Пагинация
        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = PublicHabitSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = PublicHabitSerializer(
            habits, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my(self, request):
        """Список привычек текущего пользователя"""
        habits = Habit.objects.filter(user=request.user)

        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def pleasant(self, request):
        """Список приятных привычек пользователя (для выбора в related_habit)"""
        habits = Habit.objects.filter(user=request.user, is_pleasant=True)
        serializer = PublicHabitSerializer(
            habits, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Создание привычки"""
        serializer.save(user=self.request.user)
