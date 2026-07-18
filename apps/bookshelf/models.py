from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.novels.models import Chapter, Novel


class BookshelfItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookshelf_items")
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="bookshelf_items")
    last_read_chapter = models.ForeignKey(Chapter, null=True, blank=True, on_delete=models.SET_NULL)
    reading_progress = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "novel")
        indexes = [models.Index(fields=["user", "updated_at"])]


class ReadingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_histories")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="reading_histories")
    progress_percent = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "chapter")
