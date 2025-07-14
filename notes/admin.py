from django.contrib import admin
from .models import Note, NoteCategory, Tag, NoteAttachment

class NoteAttachmentInline(admin.TabularInline):
    model = NoteAttachment
    extra = 1
    fields = ('file', 'name', 'file_type', 'file_size')
    readonly_fields = ('file_type', 'file_size')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'priority', 'is_pinned', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'is_pinned', 'category', 'tags')
    search_fields = ('title', 'snippet', 'content')
    readonly_fields = ('slug', 'uuid', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    inlines = [NoteAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'uuid', 'content', 'snippet')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'status', 'priority', 'is_pinned')
        }),
        ('User Information', {
            'fields': ('user',)
        }),
        ('Reminder', {
            'fields': ('reminder_date', 'is_reminded')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Limit notes to those belonging to the current user."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        """Set user to current user if not already set."""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(NoteCategory)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('slug',)
    
    def get_queryset(self, request):
        """Limit categories to those belonging to the current user."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        """Set user to current user if not already set."""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('slug',)
    
    def get_queryset(self, request):
        """Limit tags to those belonging to the current user."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        """Set user to current user if not already set."""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(NoteAttachment)
class NoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'note', 'file_type', 'file_size', 'created_at')
    list_filter = ('file_type',)
    search_fields = ('name', 'note__title')
    readonly_fields = ('file_type', 'file_size')
