from django.contrib import admin
from .models import Venue, Booking

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    # 'id' shows the UUID string you need for Flutter testing
    list_display = ('id', 'name', 'CityName', 'leisure', 'price_per_hour', 'user')
    list_filter = ('leisure', 'CityName')
    search_fields = ('name', 'CityName', 'StreetName')
    # This makes the UUID field visible but not editable in the detail view
    readonly_fields = ('id',) 

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'venue', 'user', 'date', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('user__username', 'venue__name')
    readonly_fields = ('created_at', 'total_price', 'end_time')