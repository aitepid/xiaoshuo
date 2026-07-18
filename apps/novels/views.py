from django.core.cache import cache
from django.db.models import F, Q
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chapter, Novel
from .serializers import ChapterDetailSerializer, ChapterListSerializer, NovelDetailSerializer, NovelListSerializer


class NovelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "summary"]
    ordering_fields = ["updated_at", "click_count", "favorite_count", "created_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return Novel.objects.filter(review_status=Novel.ReviewStatus.APPROVED).select_related("author").prefetch_related("tags")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NovelDetailSerializer
        return NovelListSerializer

    @action(detail=False, methods=["get"], url_path="rankings")
    def rankings(self, request):
        cache_key = "novel_rankings_v1"
        data = cache.get(cache_key)
        if not data:
            queryset = self.get_queryset().order_by("-click_count", "-favorite_count", "-updated_at")[:20]
            data = NovelListSerializer(queryset, many=True).data
            cache.set(cache_key, data, timeout=300)
        return Response({"results": data})


class ChapterViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        novel_id = self.kwargs.get("novel_pk")
        now = timezone.now()
        queryset = Chapter.objects.filter(
            novel_id=novel_id,
            review_status=Chapter.ReviewStatus.APPROVED,
        ).filter(
            Q(publish_status=Chapter.PublishStatus.PUBLISHED)
            | Q(publish_status=Chapter.PublishStatus.SCHEDULED, scheduled_at__lte=now)
        )
        return queryset.select_related("novel")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ChapterDetailSerializer
        return ChapterListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Novel.objects.filter(id=instance.novel_id).update(click_count=F("click_count") + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
