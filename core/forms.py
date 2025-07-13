from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'partner_type', 'profile_picture')
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'partner_type': 'نوع همسر',
            'profile_picture': 'تصویر پروفایل',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
        # Password fields
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password2'].label = 'تکرار رمز عبور'
        self.fields['password1'].help_text = 'رمز عبور باید حداقل ۸ کاراکتر باشد و شامل حروف و اعداد باشد.'
        self.fields['password2'].help_text = 'رمز عبور را مجدداً وارد کنید.'

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'profile_picture': 'تصویر پروفایل',
        }
        help_texts = {
            'profile_picture': 'تصویر پروفایل خود را انتخاب کنید (اختیاری)',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'لطفاً {self.fields[field].label} خود را وارد کنید'
            }) 