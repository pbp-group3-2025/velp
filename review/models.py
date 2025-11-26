import uuid
from django.db import models
from django.contrib.auth.models import User
from main.models import Venue


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
        """average value of criteria ratings"""
        total = self.accessibility + self.facility + self.value_for_money
        return round(total / 3, 1)

    def __str__(self):
        return f"{self.user.username} - {self.venue.name} ({self.average_rating()}/5)"