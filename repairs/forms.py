"""
Repairs forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import RepairTicket, RepairPart
from clients.models import Client
from accounts.models import User


class RepairTicketForm(forms.ModelForm):
    """Repair ticket form"""
    
    class Meta:
        model = RepairTicket
        fields = [
            'client', 'appareil', 'type_appareil', 'brand', 'model', 'serial_number',
            'device_condition', 'description_panne', 'diagnosis', 'repair_notes',
            'internal_notes', 'technicien', 'statut', 'priority',
            'cout_main_oeuvre', 'discount', 'amount_paid',
            'date_restitution_prevue', 'warranty_months', 'warranty_notes',
            'accessories', 'password', 'is_under_warranty', 'is_insured',
            'requires_approval'
        ]
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'appareil': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'type_appareil': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'device_condition': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description_panne': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'repair_notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'technicien': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'cout_main_oeuvre': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'date_restitution_prevue': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'warranty_months': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'warranty_notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
            'accessories': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
            'password': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'is_under_warranty': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'is_insured': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }


class RepairPartForm(forms.ModelForm):
    """Repair part form"""
    
    class Meta:
        model = RepairPart
        fields = [
            'repair_ticket', 'inventory_item', 'name', 'description',
            'quantity', 'unit_price', 'serial_number', 'notes'
        ]
        widgets = {
            'repair_ticket': forms.HiddenInput(),
            'inventory_item': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
        }


class RepairSearchForm(forms.Form):
    """Repair ticket search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by ticket number, client, device...')
        })
    )
    
    client = forms.ModelChoiceField(
        label=_('Client'),
        required=False,
        queryset=Client.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    technicien = forms.ModelChoiceField(
        label=_('Technician'),
        required=False,
        queryset=User.objects.filter(is_active=True, role=User.Role.TECHNICIAN),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    statut = forms.ChoiceField(
        label=_('Status'),
        required=False,
        choices=[('', _('All Statuses'))] + list(RepairTicket.Status.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    priority = forms.ChoiceField(
        label=_('Priority'),
        required=False,
        choices=[('', _('All Priorities'))] + list(RepairTicket.Priority.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    type_appareil = forms.ChoiceField(
        label=_('Device Type'),
        required=False,
        choices=[('', _('All Types'))] + list(RepairTicket.DeviceType.choices),
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


class StatusUpdateForm(forms.ModelForm):
    """Form for updating repair ticket status"""
    
    class Meta:
        model = RepairTicket
        fields = ['statut', 'notes']
        widgets = {
            'statut': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
        }


class QuickRepairForm(forms.Form):
    """Quick repair ticket form for fast entry"""
    
    client_id = forms.IntegerField(widget=forms.HiddenInput())
    appareil = forms.CharField(
        label=_('Device Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Device name')
        })
    )
    type_appareil = forms.ChoiceField(
        label=_('Device Type'),
        choices=RepairTicket.DeviceType.choices,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    description_panne = forms.CharField(
        label=_('Problem Description'),
        widget=forms.Textarea(attrs={
            'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'rows': 2,
            'placeholder': _('Describe the problem')
        })
    )
    priority = forms.ChoiceField(
        label=_('Priority'),
        choices=RepairTicket.Priority.choices,
        initial=RepairTicket.Priority.NORMAL,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
