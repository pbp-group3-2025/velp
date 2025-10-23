# reports/forms.py
from django import forms
from .models import Report

class ReportCreateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["target_type", "reason", "details", "content_type", "object_id"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details/evidence..."}),
        }

    def clean(self):
        cleaned = super().clean()
        # (Optional) prevent duplicate OPEN reports by the same user for the same target in a short timespan
        # Do this in the view where request.user is available or pass user in __init__ if you like.
        return cleaned

class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]  # reporter can update these only
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Add/adjust details..."}),
        }
