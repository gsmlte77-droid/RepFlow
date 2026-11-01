"""
Clients forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Client


class ClientForm(forms.ModelForm):
    """Client form"""
    
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'company_name', 'client_type',
            'telephone', 'secondary_telephone', 'email', 'secondary_email',
            'address', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'registration_number', 'credit_limit',
            'current_balance', 'membership_status', 'discount_rate',
            'referral_source', 'notes', 'is_active', 'is_blacklisted',
            'last_contact_date'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'client_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('e.g., +213550123456')
            }),
            'secondary_telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('e.g., +213550123456')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'secondary_email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'current_balance': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'membership_status': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'discount_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'referral_source': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'is_blacklisted': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-red-600'
            }),
            'last_contact_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
        }


class ClientSearchForm(forms.Form):
    """Client search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by name, phone, email, or company...')
        })
    )
    
    client_type = forms.ChoiceField(
        label=_('Client Type'),
        required=False,
        choices=[('', _('All Types'))] + list(Client.ClientType.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    membership_status = forms.ChoiceField(
        label=_('Membership Status'),
        required=False,
        choices=[('', _('All Statuses'))] + list(Client.MembershipStatus.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    is_active = forms.NullBooleanField(
        label=_('Active Status'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    has_balance = forms.NullBooleanField(
        label=_('Has Balance'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )


class QuickClientForm(forms.ModelForm):
    """Quick client form for fast entry"""
    
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'telephone', 'email', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('First Name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Last Name')
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Phone Number')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': _('Email (optional)')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': _('Address (optional)')
            }),
        }
