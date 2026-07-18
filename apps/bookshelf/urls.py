from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookshelfViewSet

router = DefaultRouter(trailing_slash=False)
router.register("bookshelf", BookshelfViewSet, basename="bookshelf")

urlpatterns = [
    path("", include(router.urls)),
]
