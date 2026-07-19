from rest_framework import serializers

from .models import Category, Chapter, Novel, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class NovelListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Novel
        fields = [
            "id",
            "title",
            "slug",
            "cover_url",
            "summary",
            "category",
            "status",
            "word_count",
            "click_count",
            "favorite_count",
            "rating_avg",
            "updated_at",
            "author_name",
        ]


class NovelDetailSerializer(NovelListSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta(NovelListSerializer.Meta):
        fields = NovelListSerializer.Meta.fields + ["tags", "created_at"]


class ChapterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ["id", "chapter_number", "title", "volume_title", "word_count", "published_at"]


class ChapterDetailSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source="novel.title", read_only=True)

    class Meta:
        model = Chapter
        fields = [
            "id",
            "novel",
            "novel_title",
            "chapter_number",
            "title",
            "volume_title",
            "content",
            "word_count",
            "published_at",
        ]
