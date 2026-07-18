from django.contrib import admin
from django.contrib import messages

from .models import Comment, Rating, UrgeUpdate


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "novel", "review_status", "created_at")
	list_filter = ("review_status",)
	search_fields = ("user__username", "novel__title", "content")
	actions = ("approve_selected", "reject_selected")

	@admin.action(description="一键通过选中的评论")
	def approve_selected(self, request, queryset):
		count = queryset.update(review_status="approved")
		self.message_user(request, f"已通过 {count} 条评论。", level=messages.SUCCESS)

	@admin.action(description="批量驳回选中的评论")
	def reject_selected(self, request, queryset):
		count = queryset.update(review_status="rejected")
		self.message_user(request, f"已驳回 {count} 条评论。", level=messages.WARNING)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "novel", "score", "updated_at")
	search_fields = ("user__username", "novel__title")


@admin.register(UrgeUpdate)
class UrgeUpdateAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "novel", "message", "created_at")
	search_fields = ("user__username", "novel__title", "message")
