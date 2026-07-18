from django.contrib import admin

from .models import BookshelfItem, ReadingHistory


@admin.register(BookshelfItem)
class BookshelfItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "novel", "reading_progress", "updated_at")
    search_fields = ("user__username", "novel__title")


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "chapter", "progress_percent", "updated_at")
