from django.db.models import Avg, Count
from rest_framework import serializers

from apps.novels.models import Novel

from .models import Comment, Rating, UrgeUpdate


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "novel", "chapter", "content", "review_status", "user_name", "created_at"]
        read_only_fields = ["id", "review_status", "user_name", "created_at"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "novel", "score", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        rating, _ = Rating.objects.update_or_create(
            user=user,
            novel=validated_data["novel"],
            defaults={"score": validated_data["score"]},
        )

        agg = Rating.objects.filter(novel=validated_data["novel"]).aggregate(avg=Avg("score"), cnt=Count("id"))
        Novel.objects.filter(id=validated_data["novel"].id).update(
            rating_avg=agg.get("avg") or 0,
            rating_count=agg.get("cnt") or 0,
        )
        return rating


class UrgeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrgeUpdate
        fields = ["id", "novel", "message", "created_at"]
        read_only_fields = ["id", "created_at"]
