from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Memory, MemoryImage


class MemoryImageInline(admin.TabularInline):
    model = MemoryImage
    extra = 1
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No image"
    
    image_preview.short_description = _('پیش‌نمایش')


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'mood', 'image_count', 'created_at')
    list_filter = ('mood', 'date', 'user')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    inlines = [MemoryImageInline]
    
    def image_count(self, obj):
        count = obj.images.count()
        if obj.image:
            count += 1
        return count
    
    image_count.short_description = _('تعداد تصاویر')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="auto" />', obj.image.url)
        return "No image"
    
    image_preview.short_description = _('تصویر اصلی')


@admin.register(MemoryImage)
class MemoryImageAdmin(admin.ModelAdmin):
    list_display = ('memory', 'caption', 'order', 'image_preview')
    list_filter = ('memory',)
    search_fields = ('memory__title', 'caption')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No image"
    
    image_preview.short_description = _('پیش‌نمایش')
