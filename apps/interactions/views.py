from rest_framework import mixins, permissions, viewsets

from .models import Comment, Rating, UrgeUpdate
from .serializers import CommentSerializer, RatingSerializer, UrgeUpdateSerializer


class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(review_status=Comment.ReviewStatus.APPROVED).select_related("user")
        novel_id = self.request.query_params.get("novel")
        if novel_id:
            queryset = queryset.filter(novel_id=novel_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)


class UrgeUpdateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UrgeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UrgeUpdate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
