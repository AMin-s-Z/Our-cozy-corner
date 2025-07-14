from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from notes.models import Note
from notifications.models import create_partner_notification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check for due reminders and send notifications'

    def handle(self, *args, **options):
        self.stdout.write('Checking for due reminders...')
        
        # Get current time
        now = timezone.now()
        
        # Find notes with reminders due in the last hour but not marked as reminded
        due_notes = Note.objects.filter(
            Q(reminder_date__lte=now) &
            Q(reminder_date__gte=now - timezone.timedelta(hours=1)) &
            Q(is_reminded=False)
        )
        
        self.stdout.write(f'Found {due_notes.count()} due reminders')
        
        # Process each due reminder
        for note in due_notes:
            try:
                # Get the user and their partner
                user = note.user
                
                # Import get_partner function from core.views
                from core.views import get_partner
                partner = get_partner(user)
                
                if partner:
                    # Create notification message
                    message = f"یادآوری: '{note.title}' اکنون زمان انجام آن است."
                    link = note.get_absolute_url()
                    
                    # Send notification
                    notification = create_partner_notification(
                        user=user,
                        message=message,
                        link=link
                    )
                    
                    if notification:
                        self.stdout.write(self.style.SUCCESS(
                            f'Sent reminder notification for note "{note.title}" to {partner.username}'
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'Failed to send notification for note "{note.title}"'
                        ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'No partner found for user {user.username}'
                    ))
            except Exception as e:
                logger.exception(f"Error processing reminder for note {note.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(
                    f'Error processing reminder for note "{note.title}": {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS('Reminder check completed')) 