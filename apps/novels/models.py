from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.moderation import validate_text_fields


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Novel(models.Model):
    class PublishStatus(models.TextChoices):
        ONGOING = "ongoing", "连载中"
        COMPLETED = "completed", "已完结"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="novels")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=230, unique=True, blank=True)
    cover_url = models.URLField(blank=True, default="")
    summary = models.TextField(blank=True, default="")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="novels")
    tags = models.ManyToManyField(Tag, blank=True, related_name="novels")
    status = models.CharField(max_length=16, choices=PublishStatus.choices, default=PublishStatus.ONGOING)
    review_status = models.CharField(max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    word_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["review_status", "updated_at"]),
            models.Index(fields=["click_count", "favorite_count"]),
            models.Index(fields=["category"]),
        ]

    def save(self, *args, **kwargs):
        validate_text_fields(title=self.title, summary=self.summary)
        if not self.slug:
            base = slugify(self.title)[:180] or f"novel-{timezone.now().timestamp():.0f}"
            slug = base
            suffix = 1
            while Novel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix += 1
                slug = f"{base}-{suffix}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Chapter(models.Model):
    class PublishStatus(models.TextChoices):
        DRAFT = "draft", "草稿"
        SCHEDULED = "scheduled", "定时发布"
        PUBLISHED = "published", "已发布"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="chapters")
    volume_title = models.CharField(max_length=120, blank=True, default="默认卷")
    chapter_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    publish_status = models.CharField(max_length=16, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    review_status = models.CharField(max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("novel", "chapter_number")
        ordering = ["chapter_number"]
        indexes = [
            models.Index(fields=["novel", "review_status", "publish_status"]),
            models.Index(fields=["scheduled_at"]),
        ]

    def save(self, *args, **kwargs):
        validate_text_fields(volume_title=self.volume_title, title=self.title, content=self.content)
        if self.content:
            self.word_count = len(self.content.replace("\n", "").replace(" ", ""))
        if self.publish_status == self.PublishStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.novel.title} - {self.title}"
