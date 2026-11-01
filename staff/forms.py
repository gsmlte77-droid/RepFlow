"""
Staff forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import StaffMember


class StaffMemberForm(forms.ModelForm):
    """Staff member form"""
    
    class Meta:
        model = StaffMember
        fields = [
            'user', 'employee_id', 'telephone', 'address', 'city', 'postal_code',
            'department', 'position', 'employment_status', 'hire_date', 
            'termination_date', 'salary', 'commission_rate', 'skills', 
            'specialties', 'work_schedule', 'performance_rating', 'notes', 'is_active'
        ]
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'telephone': forms.TextInput(attrs={
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
            'department': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'termination_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': _('Enter skills separated by commas')
            }),
            'specialties': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': _('Enter specialties separated by commas')
            }),
            'work_schedule': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'performance_rating': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'max': '5'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }


class StaffSearchForm(forms.Form):
    """Staff search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by name, employee ID, or department...')
        })
    )
    
    department = forms.ChoiceField(
        label=_('Department'),
        required=False,
        choices=[('', _('All Departments'))] + list(StaffMember.Department.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    employment_status = forms.ChoiceField(
        label=_('Employment Status'),
        required=False,
        choices=[('', _('All Statuses'))] + list(StaffMember.EmploymentStatus.choices),
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
