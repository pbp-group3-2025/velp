from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "venue_hint"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5, "maxlength": 500}),
            "venue_hint": forms.TextInput(attrs={"class": "form-control", "placeholder": "Venue (e.g., GBK)"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.TextInput(attrs={"class": "form-control", "placeholder": "Write a comment…", "maxlength": 300}),
        }
