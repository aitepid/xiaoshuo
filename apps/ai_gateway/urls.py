from django.urls import path

from .views import OpenAICompatCompletionsAPIView

urlpatterns = [
    path("completions", OpenAICompatCompletionsAPIView.as_view(), name="openai-compat-completions"),
]
