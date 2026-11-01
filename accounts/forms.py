"""
Accounts forms for FixSoftRepair
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class LoginForm(AuthenticationForm):
    """Custom login form with AJAX support"""
    
    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Enter your username'),
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Enter your password'),
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        label=_('Remember me'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600'
        })
    )
    
    class Meta:
        fields = ['username', 'password', 'remember_me']


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Username')
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('First Name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Last Name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Email')
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Telephone')
            }),
            'role': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Password')
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Confirm Password')
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """User update form"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'is_active', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }


class PasswordChangeCustomForm(PasswordChangeForm):
    """Custom password change form"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Current Password')
        })
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('New Password')
        })
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Confirm New Password')
        })
