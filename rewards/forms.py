from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Reward

class RewardForm(forms.ModelForm):
    """Form for creating and editing rewards."""
    
    class Meta:
        model = Reward
        fields = ['title', 'description', 'cost', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('عنوان جایزه را وارد کنید')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('توضیحات جایزه را بنویسید')
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('امتیاز مورد نیاز را وارد کنید')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': _('عنوان'),
            'description': _('توضیحات'),
            'cost': _('امتیاز'),
            'is_active': _('فعال'),
        }
        help_texts = {
            'title': _('یک عنوان کوتاه و گویا برای جایزه انتخاب کنید'),
            'description': _('جزئیات بیشتر درباره جایزه را اینجا بنویسید'),
            'cost': _('امتیاز لازم برای دریافت این جایزه'),
            'is_active': _('این جایزه در فروشگاه نمایش داده شود؟'),
        }