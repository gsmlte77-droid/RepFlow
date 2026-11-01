"""
Billing forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Invoice, InvoiceItem, Payment


class InvoiceForm(forms.ModelForm):
    """Invoice form"""
    
    class Meta:
        model = Invoice
        fields = [
            'repair_ticket', 'client', 'invoice_type', 'invoice_date', 'due_date',
            'reference', 'subtotal', 'tax_rate', 'discount', 'payment_terms',
            'notes', 'internal_notes', 'statut', 'statut_credit'
        ]
        widgets = {
            'repair_ticket': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'client': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'invoice_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'invoice_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'payment_terms': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'statut_credit': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }


class InvoiceItemForm(forms.ModelForm):
    """Invoice item form"""
    
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price', 'tax_rate', 'order']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
        }


class PaymentForm(forms.ModelForm):
    """Payment form"""
    
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'payment_method', 'reference', 'notes']
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
        }


class InvoiceSearchForm(forms.Form):
    """Invoice search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by invoice number, client, or reference...')
        })
    )
    
    client = forms.ModelChoiceField(
        label=_('Client'),
        required=False,
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    statut = forms.ChoiceField(
        label=_('Status'),
        required=False,
        choices=[('', _('All Statuses'))] + list(Invoice.Status.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    statut_credit = forms.ChoiceField(
        label=_('Credit Status'),
        required=False,
        choices=[
            ('', _('All')),
            ('SOLDE', _('Settled')),
            ('EN_COURS', _('In Progress')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    invoice_type = forms.ChoiceField(
        label=_('Invoice Type'),
        required=False,
        choices=[('', _('All Types'))] + list(Invoice.InvoiceType.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    date_from = forms.DateField(
        label=_('From Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('To Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    is_overdue = forms.NullBooleanField(
        label=_('Overdue'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    def __init__(self, *args, **kwargs):
        from clients.models import Client
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(is_active=True)


class PaymentSearchForm(forms.Form):
    """Payment search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by invoice number or reference...')
        })
    )
    
    invoice = forms.ModelChoiceField(
        label=_('Invoice'),
        required=False,
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    payment_method = forms.ChoiceField(
        label=_('Payment Method'),
        required=False,
        choices=[('', _('All Methods'))] + list(Payment.PaymentMethod.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    date_from = forms.DateField(
        label=_('From Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('To Date'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        from .models import Invoice
        super().__init__(*args, **kwargs)
        self.fields['invoice'].queryset = Invoice.objects.all()
