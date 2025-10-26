from django.forms import ModelForm
from main.models import Venue, Booking
from django import forms
from datetime import date, time, datetime


class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ["CityName", "StreetName", "leisure", "name"]

PAYMENT_CHOICES = [
    ("CASH", "Cash"),
    ("VISA", "Visa"),
    ("MASTERCARD", "MasterCard"),
    ("GOPAY", "GoPay"),
    ("PAYPAL", "PayPal"),
    ("OTHER", "Other"),
]

START_HOUR_CHOICES = [(str(i), f"{i:02d}:00") for i in range(24)]

class BookingForm(forms.ModelForm):
    # use an hour dropdown (0..23) to keep slot granularity simple
    start_hour = forms.ChoiceField(choices=START_HOUR_CHOICES, label="Start hour")
    duration_hours = forms.IntegerField(min_value=1, initial=1, label="Duration (hours)")
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, required=True)

    class Meta:
        model = Booking
        # we don't use model's start_time directly in the form, so exclude it
        fields = ["date"]  # base fields; start_time will be derived from start_hour on save

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_date(self):
        d = self.cleaned_data['date']
        if d < date.today():
            # Move this later into non-field errors — return None for now so clean() catches it
            self._past_date_error = "Cannot book a date in the past."
        return d

    def clean(self):
        cleaned = super().clean()
        errors = []

        # --- move past date error into non-field section
        if hasattr(self, "_past_date_error"):
            errors.append(self._past_date_error)

        d = cleaned.get("date")
        start_hour = cleaned.get("start_hour")
        duration = cleaned.get("duration_hours")

        if not d or start_hour is None or duration is None:
            if errors:
                raise forms.ValidationError(errors)
            return cleaned

        start_hour = int(start_hour)
        duration = int(duration)

        # crossing midnight
        if start_hour + duration > 24:
            errors.append("Booking must not cross midnight (end hour must be ≤ 24).")

        # same-day past time
        today = date.today()
        now = datetime.now()

        if d == today and start_hour < now.hour:
            errors.append(
                f"Cannot book hour {start_hour:02d}:00 — that time has already passed today."
            )

        if errors:
            raise forms.ValidationError(errors)

        return cleaned

    def save(self, venue: Venue, user, commit=True):
        # Build Booking instance from form data
        b = super().save(commit=False)
        start_hour = int(self.cleaned_data['start_hour'])
        duration = int(self.cleaned_data['duration_hours'])
        b.user = user
        b.venue = venue
        b.duration_hours = duration
        b.start_time = time(hour=start_hour, minute=0)
        # end_time and total_price will be computed in Booking.save()
        b.payment_method = self.cleaned_data.get('payment_method')
        # compute total_price here optionally
        # b.total_price = venue.price_per_hour * duration
        if commit:
            b.save()
        return b
