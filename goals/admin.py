from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'progress', 'deadline', 'completed', 'created_by')
    list_filter = ('category', 'priority', 'completed', 'created_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('priority', 'progress', 'completed')
