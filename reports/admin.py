from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_name", "content_type", "object_id","reason", "status", "reporter", "created_at")
    list_filter = ("status", "target_type", "reason", "content_type")
    search_fields = ("target_name", "details", "reporter__username")
    actions = ["mark_under_review", "mark_resolved", "mark_rejected"]

    def mark_under_review(self, request, queryset):
        queryset.update(status=Report.Status.UNDER_REVIEW)
    def mark_resolved(self, request, queryset):
        queryset.update(status=Report.Status.RESOLVED)
    def mark_rejected(self, request, queryset):
        queryset.update(status=Report.Status.REJECTED)