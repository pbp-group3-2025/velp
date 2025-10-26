# manage_staff.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Manage staff users for report moderation (main app)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to modify')
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove admin status instead of adding it',
        )

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            if options['remove']:
                user.is_staff = False
                user.is_superuser = False
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully removed staff status from {username}')
                )
            else:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully made {username} a staff member')
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist')
            )