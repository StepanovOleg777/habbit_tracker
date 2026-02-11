from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    """Регистрация пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    """Авторизация пользователя"""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
