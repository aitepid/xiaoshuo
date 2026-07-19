from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, RatingViewSet, UrgeUpdateViewSet

router = DefaultRouter(trailing_slash=True)
router.register("comments", CommentViewSet, basename="comments")
router.register("ratings", RatingViewSet, basename="ratings")
router.register("urge-updates", UrgeUpdateViewSet, basename="urge-updates")

urlpatterns = [
    path("", include(router.urls)),
]
