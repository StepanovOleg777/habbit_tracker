from django.urls import path
from .views import UserCreateView, CustomTokenObtainPairView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
]
