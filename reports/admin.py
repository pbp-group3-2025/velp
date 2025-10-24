from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_name", "content_type", "object_id", "reason", "status", "reporter", "created_at")
    list_filter = ("status", "target_type", "reason", "content_type")

    # search_fields must reference real fields/lookups (not callables)
    # "=object_id" makes exact match (good for numbers); others are icontains
    search_fields = ("details", "reporter__username", "content_type__model", "=object_id")

    actions = ["mark_under_review", "mark_resolved", "mark_rejected"]

    # --- callables used in list_display ---

    @admin.display(description="Target", ordering="object_id")
    def target_name(self, obj):
        """Human-readable name for the reported object."""
        # If you have a GenericForeignKey named `target`:
        if hasattr(obj, "target") and obj.target:
            return str(obj.target)
        # Fallback if target cannot be resolved (deleted/missing)
        if getattr(obj, "content_type", None) and getattr(obj, "object_id", None):
            return f"{obj.content_type} #{obj.object_id}"
        return "-"

    @admin.display(description="Type", ordering="content_type")
    def target_type(self, obj):
        """Short type label for the reported object (e.g., 'venue', 'review')."""
        ct = getattr(obj, "content_type", None)
        return ct.model if ct else "-"

    # --- bulk actions ---

    @admin.action(description="Mark as Under Review")
    def mark_under_review(self, request, queryset):
        queryset.update(status=Report.Status.UNDER_REVIEW)

    @admin.action(description="Mark as Resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status=Report.Status.RESOLVED)

    @admin.action(description="Mark as Rejected")
    def mark_rejected(self, request, queryset):
        queryset.update(status=Report.Status.REJECTED)
