from rest_framework import serializers

from apps.novels.models import Novel

from .models import BookshelfItem


class BookshelfItemSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source="novel.title", read_only=True)

    class Meta:
        model = BookshelfItem
        fields = [
            "id",
            "novel",
            "novel_title",
            "last_read_chapter",
            "reading_progress",
            "last_read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "novel_title"]

    def validate_novel(self, value: Novel):
        if value.review_status != value.ReviewStatus.APPROVED:
            raise serializers.ValidationError("仅可加入已审核通过的书籍。")
        return value
