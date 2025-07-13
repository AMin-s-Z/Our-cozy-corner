from django.contrib import admin
from django.contrib import messages
from .models import Notification
from .webhook import send_telegram_notification


def test_webhook(modeladmin, request, queryset):
    """Admin action to test webhook notification"""
    if not queryset:
        messages.error(request, "No notifications selected")
        return
    
    notification = queryset.first()
    try:
        result = send_telegram_notification(
            user_id=notification.recipient.id,
            message=f"Test notification from admin: {notification.message[:50]}...",
            link=notification.link
        )
        
        if result:
            messages.success(request, "Webhook test notification sent successfully")
        else:
            messages.error(request, "Failed to send webhook notification. Check server logs for details.")
    except Exception as e:
        messages.error(request, f"Error sending webhook notification: {str(e)}")

test_webhook.short_description = "Test webhook with selected notification"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'recipient')
    search_fields = ('recipient__username', 'message')
    actions = [test_webhook]