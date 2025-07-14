from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

class NoteCategory(models.Model):
    """Model for categorizing notes"""
    name = models.CharField(_('نام دسته‌بندی'), max_length=100)
    slug = models.SlugField(_('اسلاگ'), max_length=120, unique=True, allow_unicode=True, blank=True)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    icon = models.CharField(_('آیکون'), max_length=50, blank=True, help_text=_('کلاس Font Awesome مانند fa-book'))
    color = models.CharField(_('رنگ'), max_length=20, blank=True, help_text=_('کد رنگ مانند #FF4081'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='note_categories',
        verbose_name=_('کاربر')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('دسته‌بندی یادداشت')
        verbose_name_plural = _('دسته‌بندی‌های یادداشت')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('notes:category_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    """Model for tagging notes"""
    name = models.CharField(_('نام برچسب'), max_length=50)
    slug = models.SlugField(_('اسلاگ'), max_length=70, unique=True, allow_unicode=True, blank=True)
    color = models.CharField(_('رنگ'), max_length=20, blank=True, help_text=_('کد رنگ مانند #FF4081'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='note_tags',
        verbose_name=_('کاربر')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب‌ها')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('notes:tag_detail', kwargs={'slug': self.slug})

class Note(models.Model):
    """Model for professional notes with rich content"""
    
    STATUS_CHOICES = [
        ('draft', _('پیش‌نویس')),
        ('published', _('منتشر شده')),
        ('archived', _('بایگانی شده')),
    ]
    
    PRIORITY_CHOICES = [
        (1, _('کم')),
        (2, _('متوسط')),
        (3, _('زیاد')),
        (4, _('بسیار زیاد')),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('عنوان'), max_length=255)
    slug = models.SlugField(_('اسلاگ'), max_length=280, unique=True, allow_unicode=True, blank=True)
    content = RichTextUploadingField(_('متن یادداشت'))
    snippet = models.TextField(_('خلاصه'), blank=True, help_text=_('خلاصه‌ای کوتاه از یادداشت'))
    
    category = models.ForeignKey(
        NoteCategory,
        on_delete=models.SET_NULL,
        related_name='notes',
        verbose_name=_('دسته‌بندی'),
        blank=True,
        null=True
    )
    
    tags = models.ManyToManyField(
        Tag,
        related_name='notes',
        verbose_name=_('برچسب‌ها'),
        blank=True
    )
    
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    priority = models.IntegerField(
        _('اولویت'),
        choices=PRIORITY_CHOICES,
        default=2
    )
    
    is_pinned = models.BooleanField(_('سنجاق شده'), default=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('کاربر')
    )
    
    reminder_date = models.DateTimeField(_('یادآوری'), blank=True, null=True)
    is_reminded = models.BooleanField(_('یادآوری شده'), default=False)
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('یادداشت')
        verbose_name_plural = _('یادداشت‌ها')
        ordering = ['-is_pinned', '-priority', '-created_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.title, allow_unicode=True)}-{str(self.uuid)[:8]}"
        
        # Generate snippet if not provided
        if not self.snippet and self.content:
            # Remove HTML tags for snippet
            from django.utils.html import strip_tags
            text = strip_tags(self.content)
            self.snippet = text[:200] + ('...' if len(text) > 200 else '')
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('notes:detail', kwargs={'slug': self.slug})
    
    @property
    def is_due_soon(self):
        """Return True if the note has a reminder date coming up soon."""
        if not self.reminder_date:
            return False
        
        import datetime
        from django.utils import timezone
        now = timezone.now()
        soon = now + datetime.timedelta(days=1)
        return now <= self.reminder_date <= soon
    
    @property
    def is_overdue(self):
        """Return True if the note's reminder date has passed without being marked as reminded."""
        if not self.reminder_date or self.is_reminded:
            return False
        
        from django.utils import timezone
        return self.reminder_date < timezone.now()

class NoteAttachment(models.Model):
    """Model for storing file attachments for notes"""
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('یادداشت')
    )
    file = models.FileField(_('فایل'), upload_to='notes/attachments/%Y/%m/')
    name = models.CharField(_('نام فایل'), max_length=255)
    file_type = models.CharField(_('نوع فایل'), max_length=50, blank=True)
    file_size = models.IntegerField(_('حجم فایل'), default=0, help_text=_('حجم به بایت'))
    created_at = models.DateTimeField(_('تاریخ آپلود'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('پیوست یادداشت')
        verbose_name_plural = _('پیوست‌های یادداشت')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Set file type based on extension
        if self.file and not self.file_type:
            import os
            filename, extension = os.path.splitext(self.file.name)
            self.file_type = extension[1:].lower() if extension else 'unknown'
            
            # Set filename if not provided
            if not self.name:
                self.name = os.path.basename(filename)
                
            # Get file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
                
        super().save(*args, **kwargs)
