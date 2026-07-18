from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginAPIView, ProfileAPIView, RegisterAPIView

urlpatterns = [
    path("auth/register", RegisterAPIView.as_view(), name="register"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me", ProfileAPIView.as_view(), name="profile"),
]
