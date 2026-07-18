from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.novels.models import Chapter, Novel
from apps.moderation import validate_text_fields


class Comment(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="comments")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    content = models.TextField()
    review_status = models.CharField(max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        validate_text_fields(content=self.content)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "novel")


class UrgeUpdate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="urge_updates")
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="urge_updates")
    message = models.CharField(max_length=255, blank=True, default="作者快更新")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        validate_text_fields(message=self.message)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
