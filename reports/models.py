# reports/models.py
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q, UniqueConstraint

class Report(models.Model):
    class TargetType(models.TextChoices):
        VENUE = "venue", "Venue"
        REVIEW = "review", "Review"
        POST = "post", "Post"
        COMMENT = "comment", "Comment"
        COMMUNITY = "community", "Community"
        

    class Reason(models.TextChoices):
        INAPPROPRIATE = "inappropriate", "Inappropriate / Harassment"
        SPAM = "spam", "Spam / Ads"
        FALSE_INFO = "false_info", "False or Misleading Info"
        SCAM = "scam", "Scam / Fraud"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        UNDER_REVIEW = "under_review", "Under Review"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"

    # reporter
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")

    # generic target
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)  # accepts ints or UUIDs as string
    target = GenericForeignKey("content_type", "object_id")

    target_type = models.CharField(max_length=20, choices=TargetType.choices)
    reason = models.CharField(max_length=30, choices=Reason.choices)
    details = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="handled_reports"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_locked(self) -> bool:
        return self.status in (self.Status.RESOLVED, self.Status.REJECTED)

    def set_status(self, new_status, by_user):
        self.status = new_status
        self.handled_by = by_user
        if new_status == self.Status.RESOLVED:
            self.resolved_at = timezone.now()
        self.save(update_fields=["status", "handled_by", "resolved_at"])

    @property
    def target_name(self) -> str:
        """
        Try common name-like attributes across apps; fall back to __str__.
        Works for Venue (name), Post (title), User (username), etc.
        """
        obj = self.target
        if not obj:
            return "-"
        for attr in ("name", "title", "username"):
            val = getattr(obj, attr, None)
            if val:
                return str(val)
        return str(obj)  # fallback to __str__

    class Meta:
        db_table = "reports"
        indexes = [
            models.Index(fields=["content_type", "object_id", "status"]),
        ]

        unique_together = [
            ['reporter', 'content_type', 'object_id', 'status']
        ]

        constraints = [
            # only ONE OPEN per (user, target)
            UniqueConstraint(
                fields=["reporter", "content_type", "object_id"],
                condition=Q(status="open"),
                name="uq_open_report_per_user_target",
            ),
        ]