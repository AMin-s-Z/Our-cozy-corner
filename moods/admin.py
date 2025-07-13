from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Mood

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood_type', 'rating', 'created_at')
    list_filter = ('mood_type', 'rating', 'date', 'user')
    search_fields = ('notes', 'user__username')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
