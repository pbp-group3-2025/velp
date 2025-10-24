import uuid
import datetime
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
   
    price_per_hour = models.IntegerField(default=250000, help_text="Price per hour in IDR (e.g. 250000)")

    def __str__(self):
        return self.name


# Booking
class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]
    
    PAYMENT_CHOICES = [
        ("CASH", "Cash"),
        ("VISA", "Visa"),
        ("MASTERCARD", "MasterCard"),
        ("GOPAY", "GoPay"),
        ("PAYPAL", "PayPal"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.PositiveIntegerField(default=1)
    total_price = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ("venue", "date", "start_time", "end_time")
        ordering = ['-date', 'start_time']

    def __str__(self):
        return f"{self.venue.name} - {self.date} {self.start_time}-{self.end_time} by {self.user.username}"
    
    def compute_total_price(self):
        """Compute based on venue.price_per_hour * duration"""
        price = getattr(self.venue, 'price_per_hour', 0) or 0
        return int(price * self.duration_hours)

    def save(self, *args, **kwargs):
        # ensure total_price and end_time will be set if start_time and duration present
        if self.start_time and self.duration_hours:
            # compute end_time: only hour-based slots (we assume exact hours)
            start_hour = self.start_time.hour
            end_hour = (start_hour + self.duration_hours) % 24
            # construct end_time with same minute/second as start (00:00)
            self.end_time = datetime.time(hour=end_hour, minute=0)
        # compute price
        if self.venue:
            self.total_price = self.compute_total_price()
        super().save(*args, **kwargs)
