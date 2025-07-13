from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'recipient')
    search_fields = ('recipient__username', 'message')