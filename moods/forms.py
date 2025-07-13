from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Mood

class MoodForm(forms.ModelForm):
    """Form for creating and updating mood entries."""
    class Meta:
        model = Mood
        fields = ['mood_type', 'rating', 'notes']
        widgets = {
            'mood_type': forms.RadioSelect(),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10, 'type': 'range'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'یادداشت‌های خود را اینجا بنویسید...'}),
        }
        help_texts = {
            'mood_type': _('حال و هوای امروز خود را انتخاب کنید'),
            'notes': _('یادداشت‌های اختیاری در مورد حال و هوای امروز خود')
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if field_name != 'mood_type':  # Skip mood_type as it's handled differently
                field.widget.attrs['class'] = 'form-control'
            
        # Add range slider for rating
        self.fields['rating'].widget.attrs.update({
            'class': 'form-range', 
            'step': '1'
        })
        
        # Add special styling for notes
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'style': 'resize: none;'
        }) 