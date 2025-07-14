from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Memory, MemoryImage

class MemoryForm(forms.ModelForm):
    """Form for creating and updating memories."""
    class Meta:
        model = Memory
        fields = ['title', 'content', 'image', 'mood', 'date', 'location']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'gregorian-date form-control',
                'autocomplete': 'off',
                'data-jdp': '',
                'placeholder': 'انتخاب تاریخ'
            }),
            'content': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            # Add class for icon padding
            if field_name in ['title', 'location']:
                field.widget.attrs['class'] += ' form-control-icon'
        
        # Make the image field optional and add help text
        self.fields['image'].required = False
        self.fields['image'].help_text = _('تصویر اصلی خاطره (اختیاری)')


class MemoryImageForm(forms.ModelForm):
    """Form for creating and updating memory images."""
    class Meta:
        model = MemoryImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        } 