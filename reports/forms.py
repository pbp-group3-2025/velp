# reports/forms.py
from django import forms
from .models import Report

class ReportCreateForm(forms.ModelForm):
    class Meta:
        model = Report
        # ⬇️ no content_type here
        fields = ["target_type", "reason", "details", "object_id"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details/evidence..."}),
        }

    def clean_object_id(self):
        oid = self.cleaned_data["object_id"]
        if oid <= 0:
            raise forms.ValidationError("Invalid object id.")
        return oid

class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4, "placeholder": "Add/adjust details..."}),
        }