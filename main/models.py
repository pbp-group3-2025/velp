import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.conf import settings  # for AUTH_USER_MODEL

# Venue
class Venue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    LEISURE_CHOICES = [
        ('pitch', 'Pitch'),
        ('stadium', 'Stadium'),
        ('sports_centre', 'Sports Centre'),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CityName = models.CharField(max_length=255)
    StreetName = models.TextField()
    leisure = models.CharField(max_length=20, choices=LEISURE_CHOICES, default='pitch')
    name = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return self.name

