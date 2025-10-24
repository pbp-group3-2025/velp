from django.forms import ModelForm
from community.models import Community


class CommunityForm(ModelForm):
    class Meta:
        model = Community
        fields = ["title", "description"]
