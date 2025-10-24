from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['accessibility', 'facility', 'value_for_money', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How was your experience?'}),
        }