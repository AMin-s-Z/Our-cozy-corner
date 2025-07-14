from django import forms
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Note, NoteCategory, Tag, NoteAttachment

class NoteForm(forms.ModelForm):
    """Form for creating and updating notes."""
    
    category_new = forms.CharField(
        label=_('دسته‌بندی جدید'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('نام دسته‌بندی جدید'),
            'class': 'form-control'
        })
    )
    
    tags_new = forms.CharField(
        label=_('برچسب‌های جدید'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('برچسب‌های جدید (با کاما جدا کنید)'),
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'snippet', 'category', 'tags', 'status', 'priority', 'is_pinned', 'reminder_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('عنوان یادداشت')}),
            'content': CKEditorUploadingWidget(config_name='default'),
            'snippet': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('خلاصه یادداشت (اختیاری)')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select select2', 'data-placeholder': _('برچسب‌ها را انتخاب کنید')}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_date': forms.DateTimeInput(attrs={'class': 'form-control datepicker', 'placeholder': _('تاریخ یادآوری')})
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Limit queryset for user-specific fields
        if user:
            self.fields['category'].queryset = NoteCategory.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Handle new category
        category_new = cleaned_data.get('category_new')
        if category_new and not cleaned_data.get('category'):
            # Create new category
            category, created = NoteCategory.objects.get_or_create(
                name=category_new,
                user=self.user
            )
            cleaned_data['category'] = category
        
        # Handle new tags
        tags_new = cleaned_data.get('tags_new')
        if tags_new:
            # Split by comma and create tags that don't exist
            tag_names = [t.strip() for t in tags_new.split(',') if t.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    user=self.user
                )
                # Add to m2m field - needs instance to be saved first
                if self.instance.pk:
                    self.instance.tags.add(tag)
                else:
                    # For new notes, remember tags to add after save
                    if not hasattr(self, '_new_tags'):
                        self._new_tags = []
                    self._new_tags.append(tag)
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        # Add saved tags for new instances
        if hasattr(self, '_new_tags') and commit:
            for tag in self._new_tags:
                instance.tags.add(tag)
        
        return instance

class NoteAttachmentForm(forms.ModelForm):
    """Form for uploading attachments to notes."""
    class Meta:
        model = NoteAttachment
        fields = ['file', 'name']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('نام فایل (اختیاری)')})
        }

class NoteCategoryForm(forms.ModelForm):
    """Form for creating and updating note categories."""
    class Meta:
        model = NoteCategory
        fields = ['name', 'description', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('نام دسته‌بندی')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('توضیحات (اختیاری)')}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('کلاس Font Awesome مانند fa-book')}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker', 'placeholder': _('کد رنگ مانند #FF4081')})
        }

class TagForm(forms.ModelForm):
    """Form for creating and updating tags."""
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('نام برچسب')}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker', 'placeholder': _('کد رنگ مانند #FF4081')})
        }

class NoteFilterForm(forms.Form):
    """Form for filtering notes."""
    STATUS_CHOICES = [('', _('همه وضعیت‌ها'))] + list(Note.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', _('همه اولویت‌ها'))] + list(Note.PRIORITY_CHOICES)
    SORT_CHOICES = [
        ('created_at', _('تاریخ ایجاد (جدید به قدیم)')),
        ('-created_at', _('تاریخ ایجاد (قدیم به جدید)')),
        ('title', _('عنوان (الف تا ی)')),
        ('-title', _('عنوان (ی تا الف)')),
        ('priority', _('اولویت (کم به زیاد)')),
        ('-priority', _('اولویت (زیاد به کم)'))
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('جستجو...')})
    )
    
    category = forms.ModelChoiceField(
        queryset=NoteCategory.objects.none(),
        required=False,
        empty_label=_('همه دسته‌بندی‌ها'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    has_reminder = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_pinned = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = NoteCategory.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user) 