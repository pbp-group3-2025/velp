from django.contrib import admin
from .models import Report # Import your model

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    # This makes the UUID (id) and other fields visible in the list
    list_display = ('id', 'target_type', 'target_name', 'reason', 'status')