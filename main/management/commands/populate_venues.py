import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Venue  # Import your Venue model
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates the Venue model from a venues.csv file'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate venues...'))

        # --- 1. Find the default user to assign ---
        default_user = None
        try:
            default_user = User.objects.get(username="ADMIN") # Using the user from your log
        except User.DoesNotExist:
            default_user = User.objects.first() # Fallback
        
        if not default_user:
            self.stdout.write(self.style.ERROR('No users found. Please create a superuser first.'))
            self.stdout.write(self.style.ERROR('Run: python manage.py createsuperuser'))
            return

        self.stdout.write(f'All new venues will be assigned to user: {default_user.username}')

        # --- 2. Define the path to the CSV file ---
        # Using the filename from your last error
        csv_file_path = os.path.join(settings.BASE_DIR, 'jakarta_soccer_minimal_no_duplicate.csv') 

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'Error: File not found at {csv_file_path}'))
            return

        # --- 3. Open and read the CSV ---
        self.stdout.write('Clearing old venue data...')
        Venue.objects.all().delete()
        
        venue_count = 0
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file) 

                for row in reader:
                    # --- 4. Map CSV columns to your model fields ---
                    # We use 'name' as the unique key for get_or_create
                    venue, created = Venue.objects.get_or_create(
                        name=row['name'],
                        defaults={
                            # This is the fix:
                            'StreetName': row['StreetName'], # Was 'address'
                            
                            # Adding the other fields from your model/CSV:
                            'CityName': row['CityName'],
                            'leisure': row['leisure'],
                            'user': default_user,
                        }
                    )
                    
                    if created:
                        venue_count += 1

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully created {venue_count} new venues! ✅'))