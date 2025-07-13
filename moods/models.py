from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Mood(models.Model):
    """Model for tracking daily emotional moods with rating and notes."""
    
    MOOD_CHOICES = [
        ('very_happy', _('بسیار خوشحال')),
        ('happy', _('خوشحال')),
        ('excited', _('هیجان‌زده')),
        ('content', _('راضی')),
        ('relaxed', _('آرام')),
        ('neutral', _('معمولی')),
        ('confused', _('سردرگم')),
        ('anxious', _('مضطرب')),
        ('sad', _('غمگین')),
        ('frustrated', _('کلافه')),
        ('angry', _('عصبانی')),
        ('sleepy', _('خواب‌آلود')),
        ('very_sad', _('بسیار غمگین')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='moods',
        verbose_name=_('کاربر')
    )
    date = models.DateField(_('تاریخ'), auto_now_add=True)
    mood_type = models.CharField(_('نوع حال و هوا'), max_length=20, choices=MOOD_CHOICES)
    rating = models.IntegerField(
        _('امتیاز'), 
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text=_('حال و هوای خود را از 1 (بدترین) تا 10 (بهترین) امتیاز دهید')
    )
    notes = models.TextField(_('یادداشت‌ها'), blank=True, null=True)
    created_at = models.DateTimeField(_('زمان ایجاد'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('حال و هوا')
        verbose_name_plural = _('حال و هوا')
        ordering = ['-date', '-created_at']
        # Ensure only one mood entry per user per day
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_mood_type_display()} ({self.date})"
    
    def get_mood_emoji(self):
        """Return the emoji for the mood."""
        emojis = {
            'very_happy': '😁',
            'happy': '😊',
            'excited': '🤩',
            'content': '🙂',
            'relaxed': '😌',
            'neutral': '😐',
            'confused': '😕',
            'anxious': '😟',
            'sad': '😢',
            'frustrated': '😤',
            'angry': '😡',
            'sleepy': '😴',
            'very_sad': '😭',
        }
        return emojis.get(self.mood_type, '😐')
        
    def get_rating_color(self):
        """Return the CSS class for the rating."""
        if self.rating >= 8:
            return 'text-success'
        elif self.rating >= 6:
            return 'text-info'
        elif self.rating >= 4:
            return 'text-warning'
        else:
            return 'text-danger'
