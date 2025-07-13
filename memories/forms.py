from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Memory

class MemoryForm(forms.ModelForm):
    """Form for creating and updating memories."""
    class Meta:
        model = Memory
        fields = ['title', 'content', 'image', 'mood', 'date', 'location']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'persian-date form-control',
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