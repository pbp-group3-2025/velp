import uuid
from django.db import models
from django.contrib.auth.models import User


#A supprimer quand le vrai modèle Venue sera disponible
# A remplacer par from venues.models import Venue
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


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 à 5

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')

    accessibility = models.IntegerField(choices=RATING_CHOICES)
    facility = models.IntegerField(choices=RATING_CHOICES)
    value_for_money = models.IntegerField(choices=RATING_CHOICES)

    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        """Calcule la moyenne des critères."""
        total = self.accessibility + self.facility + self.value_for_money
        return round(total / 3, 1)

    def __str__(self):
        return f"{self.user.username} - {self.venue.name} ({self.average_rating()}/5)"