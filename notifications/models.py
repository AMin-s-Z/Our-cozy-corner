from django.db import models
from django.conf import settings


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'Notification for {self.recipient.username} - {self.message[:20]}'

    class Meta:
        ordering = ['-timestamp']


def create_partner_notification(user, message, link=None):
    """
    Helper function to create notifications for partners.
    
    Args:
        user: The user performing the action
        message: The notification message
        link: Optional link to redirect to when the notification is clicked
        
    Returns:
        The created Notification object or None if no partner exists
    """
    # Import here to avoid circular imports
    from core.views import get_partner
    
    # Use try/except to handle the import error gracefully
    try:
        from .webhook import send_telegram_notification
        send_telegram = True
    except ImportError:
        send_telegram = False
    
    partner = get_partner(user)
    if partner:
        # Send notification to Telegram if available
        if send_telegram:
            try:
                send_telegram_notification(
                    user_id=partner.id,
                    message=message,
                    link=link
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send Telegram notification: {str(e)}")
        
        # Store notification in database
        return Notification.objects.create(
            recipient=partner,
            message=message,
            link=link
        )
    return None