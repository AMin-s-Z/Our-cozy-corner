from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Memory(models.Model):
    """Model for storing memories with text, images and emotional moods."""
    
    MOOD_CHOICES = [
        ('happy', _('شاد')),
        ('love', _('عاشقانه')),
        ('excited', _('هیجان‌زده')),
        ('relaxed', _('آرام')),
        ('content', _('راضی')),
        ('sad', _('غمگین')),
        ('angry', _('عصبانی')),
        ('neutral', _('خنثی')),
        ('surprised', _('متعجب')),
        ('laughing', _('خندان')),
        ('cool', _('باحال')),
        ('silly', _('شوخ')),
        ('thinking', _('متفکر')),
    ]
    
    title = models.CharField(_('عنوان'), max_length=200)
    content = models.TextField(_('متن خاطره'))
    # Keep the single image field for backward compatibility, but mark as deprecated
    image = models.ImageField(_('تصویر (قدیمی)'), upload_to='memories/', blank=True, null=True, 
                            help_text=_('این فیلد برای سازگاری با نسخه‌های قبلی حفظ شده است. لطفاً از قابلیت آپلود چند تصویر استفاده کنید.'))
    mood = models.CharField(_('حس و حال'), max_length=20, choices=MOOD_CHOICES, default='content')
    date = models.DateField(_('تاریخ'))
    location = models.CharField(_('مکان'), max_length=255, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='memories',
        verbose_name=_('کاربر')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    
    class Meta:
        verbose_name = _('خاطره')
        verbose_name_plural = _('خاطرات')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return self.title
        
    def get_mood_icon(self):
        """Return the Font Awesome icon class for the mood."""
        icons = {
            'happy': 'fa-smile',
            'love': 'fa-heart',
            'excited': 'fa-laugh-beam',
            'relaxed': 'fa-spa',
            'content': 'fa-smile-beam',
            'sad': 'fa-frown',
            'angry': 'fa-angry',
            'neutral': 'fa-meh',
            'surprised': 'fa-dizzy',
            'laughing': 'fa-laugh-squint',
            'cool': 'fa-glasses',
            'silly': 'fa-grin-tongue-wink',
            'thinking': 'fa-lightbulb',
        }
        return icons.get(self.mood, 'fa-smile')
        
    def get_mood_color(self):
        """Return the CSS color class for the mood."""
        colors = {
            'happy': 'text-warning',
            'love': 'text-danger',
            'excited': 'text-warning',
            'relaxed': 'text-info',
            'content': 'text-success',
            'sad': 'text-primary',
            'angry': 'text-danger',
            'neutral': 'text-secondary',
            'surprised': 'text-purple',
            'laughing': 'text-warning',
            'cool': 'text-primary',
            'silly': 'text-success',
            'thinking': 'text-info',
        }
        return colors.get(self.mood, 'text-dark')
        
    @property
    def primary_image(self):
        """Return the first image or the legacy image."""
        images = self.images.all()
        if images.exists():
            return images.first().image
        return self.image


class MemoryImage(models.Model):
    """Model for storing multiple images for a memory."""
    memory = models.ForeignKey(
        Memory,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('خاطره')
    )
    image = models.ImageField(_('تصویر'), upload_to='memories/')
    caption = models.CharField(_('توضیح تصویر'), max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(_('ترتیب'), default=0)
    
    class Meta:
        verbose_name = _('تصویر خاطره')
        verbose_name_plural = _('تصاویر خاطرات')
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.memory.title} - تصویر {self.order + 1}"
