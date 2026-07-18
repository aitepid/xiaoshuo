from django.core.cache import cache
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BookshelfItem
from .serializers import BookshelfItemSerializer


class BookshelfViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BookshelfItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookshelfItem.objects.filter(user=self.request.user).select_related("novel", "last_read_chapter")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="sync-progress")
    def sync_progress(self, request, pk=None):
        item = self.get_object()
        progress = float(request.data.get("reading_progress", item.reading_progress))
        chapter_id = request.data.get("last_read_chapter")
        item.reading_progress = max(0, min(progress, 100))
        item.last_read_chapter_id = chapter_id or item.last_read_chapter_id
        item.last_read_at = timezone.now()
        item.save(update_fields=["reading_progress", "last_read_chapter", "last_read_at", "updated_at"])

        cache_key = f"reading_progress:{request.user.id}:{item.novel_id}"
        cache.set(cache_key, {"reading_progress": item.reading_progress, "chapter_id": item.last_read_chapter_id}, timeout=3600)

        return Response(BookshelfItemSerializer(item).data, status=status.HTTP_200_OK)
