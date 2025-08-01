from django.db import models
from django.conf import settings
import logging

# Setup logger
logger = logging.getLogger(__name__)

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
    try:
        from core.views import get_partner
        
        # Use try/except to handle the import error gracefully
        try:
            from .webhook import send_telegram_notification
            send_telegram = True
        except ImportError:
            logger.warning("Could not import send_telegram_notification function")
            send_telegram = False
        
        partner = get_partner(user)
        if not partner:
            logger.info(f"No partner found for user {user.username} (ID: {user.id})")
            return None
            
        # Create notification in database first to ensure it's always saved
        notification = Notification.objects.create(
            recipient=partner,
            message=message,
            link=link
        )
        
        # Send notification to Telegram if available
        if send_telegram:
            try:
                telegram_result = send_telegram_notification(
                    user_id=partner.id,
                    message=message,
                    link=link
                )
                if telegram_result:
                    logger.info(f"Telegram notification sent successfully to user {partner.username}")
                else:
                    logger.warning(f"Telegram notification failed for user {partner.username}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {str(e)}")
        else:
            logger.info("Skipping Telegram notification (function not available)")
        
        return notification
    except Exception as e:
        logger.exception(f"Error in create_partner_notification: {str(e)}")
        # Still try to create the notification even if there was an error elsewhere
        try:
            if 'partner' in locals() and partner:
                return Notification.objects.create(
                    recipient=partner,
                    message=message,
                    link=link
                )
        except Exception:
            logger.exception("Failed to create notification as fallback")
        
        return None