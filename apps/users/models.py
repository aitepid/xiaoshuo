from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        READER = "reader", "读者"
        AUTHOR = "author", "作者"
        ADMIN = "admin", "管理员"

    email = models.EmailField("邮箱", unique=True, null=True, blank=True)
    phone = models.CharField("手机号", max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.READER)
    bio = models.CharField(max_length=255, blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
        ]

    @property
    def is_author(self) -> bool:
        return self.role == self.Role.AUTHOR
