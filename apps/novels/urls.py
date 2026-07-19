from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import CategoryViewSet, ChapterViewSet, NovelViewSet

router = DefaultRouter(trailing_slash=False)
router.register("categories", CategoryViewSet, basename="categories")
router.register("novels", NovelViewSet, basename="novels")

chapter_list = ChapterViewSet.as_view({"get": "list"})
chapter_detail = ChapterViewSet.as_view({"get": "retrieve"})

urlpatterns = [
    path("", include(router.urls)),
    path("novels/<int:novel_pk>/chapters", chapter_list, name="chapter-list"),
    path("novels/<int:novel_pk>/chapters/<int:pk>", chapter_detail, name="chapter-detail"),
]
