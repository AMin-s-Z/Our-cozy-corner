from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Goal(models.Model):
    """Model for tracking shared goals between partners."""
    
    CATEGORY_CHOICES = [
        ('relationship', _('رابطه')),
        ('financial', _('مالی')),
        ('health', _('سلامتی')),
        ('travel', _('سفر')),
        ('home', _('خانه')),
        ('personal', _('شخصی')),
        ('other', _('سایر')),
    ]
    
    PRIORITY_CHOICES = [
        (1, _('کم')),
        (2, _('متوسط')),
        (3, _('زیاد')),
    ]
    
    title = models.CharField(_('عنوان'), max_length=200)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    category = models.CharField(_('دسته‌بندی'), max_length=20, choices=CATEGORY_CHOICES)
    priority = models.IntegerField(_('اولویت'), choices=PRIORITY_CHOICES, default=2)
    progress = models.IntegerField(
        _('پیشرفت'), 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text=_('درصد پیشرفت از 0 تا 100')
    )
    deadline = models.DateField(_('مهلت'), null=True, blank=True)
    completed = models.BooleanField(_('تکمیل شده'), default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='created_goals',
        verbose_name=_('ایجاد شده توسط')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    
    class Meta:
        verbose_name = _('هدف')
        verbose_name_plural = _('اهداف')
        ordering = ['-priority', 'deadline', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_category_icon(self):
        """Return the Font Awesome icon class for the category."""
        icons = {
            'relationship': 'fa-heart',
            'financial': 'fa-money-bill-wave',
            'health': 'fa-heartbeat',
            'travel': 'fa-plane',
            'home': 'fa-home',
            'personal': 'fa-user',
            'other': 'fa-star',
        }
        return icons.get(self.category, 'fa-star')
    
    def get_category_color(self):
        """Return the CSS color class for the category."""
        colors = {
            'relationship': 'text-danger',
            'financial': 'text-success',
            'health': 'text-info',
            'travel': 'text-primary',
            'home': 'text-secondary',
            'personal': 'text-warning',
            'other': 'text-dark',
        }
        return colors.get(self.category, 'text-dark')
    
    def get_priority_color(self):
        """Return the CSS color class for the priority."""
        colors = {
            1: 'text-muted',
            2: 'text-primary',
            3: 'text-danger',
        }
        return colors.get(self.priority, 'text-muted')
    
    def get_progress_color(self):
        """Return the CSS color class for the progress."""
        if self.progress >= 75:
            return 'bg-success'
        elif self.progress >= 50:
            return 'bg-info'
        elif self.progress >= 25:
            return 'bg-warning'
        else:
            return 'bg-danger'
