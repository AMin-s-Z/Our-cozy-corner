from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Goal

class GoalForm(forms.ModelForm):
    """Form for creating and updating goals."""
    class Meta:
        model = Goal
        fields = ['title', 'description', 'category', 'priority', 'progress', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={
                'class': 'persian-date form-control',
                'autocomplete': 'off',
                'placeholder': 'انتخاب تاریخ',
                'readonly': 'readonly'
            }),
            'description': forms.Textarea(attrs={'rows': 3}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Add special styling for select fields
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['priority'].widget.attrs.update({'class': 'form-select'})
        
        # Add range slider for progress
        self.fields['progress'].widget.attrs.update({
            'class': 'form-range', 
            'step': '5'
        }) 