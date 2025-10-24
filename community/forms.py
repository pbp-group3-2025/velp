from django import forms
from .models import Post, Group, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['headline','content', 'image_url']
        widgets = {
            'headline': forms.TextInput(attrs={"class": "form-control",'placeholder': 'Short headline '}),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share something…', 'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://…/image.jpg (optional)', 'class': 'form-control'}),
        }

class GroupForm(forms.ModelForm):  # used for create (can also set description at create)
    class Meta:
        model = Group
        fields = ['name', 'description']   # <-- include description
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Football A', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe this group (optional)', 'class': 'form-control'}),
        }

class GroupDescriptionForm(forms.ModelForm):  # used for edit description
    class Meta:
        model = Group
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Group description…'}),
        }

class CommentForm(forms.ModelForm):       
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment…', 'class': 'form-control'}),
        }
