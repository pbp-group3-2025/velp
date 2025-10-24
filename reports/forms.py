# reports/forms.py
from django import forms
from .models import Report

from django import forms
from .models import Report
from uuid import UUID

class ReportCreateForm(forms.ModelForm):
    # override to be text-based
    object_id = forms.CharField()

    class Meta:
        model = Report
        fields = ["target_type", "reason", "details", "object_id"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details/evidence..."}),
        }

    def clean_object_id(self):
        raw = (self.cleaned_data.get("object_id") or "").strip()
        if not raw:
            raise forms.ValidationError("Invalid object id.")

        # accept positive integers
        try:
            iv = int(raw)
            if iv <= 0:
                raise forms.ValidationError("Invalid object id.")
            return raw  # store as string
        except ValueError:
            pass

        # accept UUIDs
        try:
            UUID(raw)
            return raw  # store as string
        except ValueError:
            raise forms.ValidationError("Invalid object id format.")

class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Add/adjust details..."}),
        }