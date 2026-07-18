from django.contrib import admin
from django.contrib import messages

from .models import Chapter, Novel, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "status", "review_status", "updated_at")
    list_filter = ("status", "review_status", "category")
    search_fields = ("title", "summary", "author__username")
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="一键通过选中的小说")
    def approve_selected(self, request, queryset):
        count = queryset.update(review_status=Novel.ReviewStatus.APPROVED)
        self.message_user(request, f"已通过 {count} 本小说。", level=messages.SUCCESS)

    @admin.action(description="批量驳回选中的小说")
    def reject_selected(self, request, queryset):
        count = queryset.update(review_status=Novel.ReviewStatus.REJECTED)
        self.message_user(request, f"已驳回 {count} 本小说。", level=messages.WARNING)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "novel", "chapter_number", "title", "publish_status", "review_status")
    list_filter = ("publish_status", "review_status")
    search_fields = ("title", "novel__title")
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="一键通过选中的章节")
    def approve_selected(self, request, queryset):
        count = queryset.update(review_status=Chapter.ReviewStatus.APPROVED, publish_status=Chapter.PublishStatus.PUBLISHED)
        self.message_user(request, f"已通过 {count} 个章节。", level=messages.SUCCESS)

    @admin.action(description="批量驳回选中的章节")
    def reject_selected(self, request, queryset):
        count = queryset.update(review_status=Chapter.ReviewStatus.REJECTED)
        self.message_user(request, f"已驳回 {count} 个章节。", level=messages.WARNING)
