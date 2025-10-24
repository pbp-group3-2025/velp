from django.forms import ModelForm
from main.models import Venue


class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ["CityName", "StreetName", "leisure", "name"]
