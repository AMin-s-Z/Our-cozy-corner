from django.contrib import admin
from .models import Activity, CompletedActivity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin configuration for the Activity model."""
    list_display = ('title', 'points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('points', 'is_active')
    ordering = ('-points',)

@admin.register(CompletedActivity)
class CompletedActivityAdmin(admin.ModelAdmin):
    """Admin configuration for the CompletedActivity model."""
    list_display = ('user', 'activity', 'completed_at')
    list_filter = ('activity',)
    search_fields = ('user__username', 'activity__title')
    readonly_fields = ('user', 'activity', 'completed_at')
    ordering = ('-completed_at',)

    def has_add_permission(self, request):
        # Completed activities should not be manually added from the admin
        return False