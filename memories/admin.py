from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Memory

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'mood', 'created_at')
    list_filter = ('mood', 'date', 'user')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
