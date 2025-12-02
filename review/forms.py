from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['accessibility', 'facility', 'value_for_money', 'comment']
        widgets = {
            'accessibility': forms.Select(attrs={'id': 'id_accessibility'}),
            'facility': forms.Select(attrs={'id': 'id_facility'}),
            'value_for_money': forms.Select(attrs={'id': 'id_value_for_money'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'How was your experience?'}),
        }