"""
Config forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import AppConfig


class CompanyInfoForm(forms.ModelForm):
    """Company information form"""
    
    class Meta:
        model = AppConfig
        fields = [
            'company_name', 'company_slogan', 'phone', 'email', 'website',
            'address', 'city', 'postal_code', 'country', 'logo', 'favicon'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'company_slogan': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }


class FinancialSettingsForm(forms.ModelForm):
    """Financial settings form"""
    
    class Meta:
        model = AppConfig
        fields = [
            'currency', 'tax_rate', 'discount_rate',
            'invoice_prefix', 'invoice_start_number',
            'invoice_footer_text', 'invoice_terms'
        ]
        widgets = {
            'currency': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'discount_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'invoice_prefix': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'invoice_start_number': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'invoice_footer_text': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'invoice_terms': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 5
            }),
        }


class LocalizationForm(forms.ModelForm):
    """Localization form"""
    
    class Meta:
        model = AppConfig
        fields = ['default_language', 'timezone', 'date_format']
        widgets = {
            'default_language': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'date_format': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }


class BusinessSettingsForm(forms.ModelForm):
    """Business settings form"""
    
    class Meta:
        model = AppConfig
        fields = [
            'business_hours', 'max_credit_days', 'credit_enabled',
            'low_stock_threshold', 'email_notifications', 'sms_notifications',
            'system_name', 'version', 'maintenance_mode'
        ]
        widgets = {
            'business_hours': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'max_credit_days': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'credit_enabled': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'system_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'maintenance_mode': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }
