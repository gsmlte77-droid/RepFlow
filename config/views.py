"""
Config views for FixSoftRepair
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from accounts.models import User
from .models import AppConfig
from .forms import (
    CompanyInfoForm, FinancialSettingsForm,
    LocalizationForm, BusinessSettingsForm
)


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_admin()


@login_required
@user_passes_test(is_admin)
def config_view(request):
    """Main configuration view"""
    config = AppConfig.get_instance()
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'company_info':
            form = CompanyInfoForm(request.POST, request.FILES, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, _('Company information updated successfully!'))
        
        elif form_type == 'financial_settings':
            form = FinancialSettingsForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, _('Financial settings updated successfully!'))
        
        elif form_type == 'localization':
            form = LocalizationForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, _('Localization settings updated successfully!'))
        
        elif form_type == 'business_settings':
            form = BusinessSettingsForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, _('Business settings updated successfully!'))
        
        return redirect('config:config')
    
    # Initialize forms
    company_form = CompanyInfoForm(instance=config)
    financial_form = FinancialSettingsForm(instance=config)
    localization_form = LocalizationForm(instance=config)
    business_form = BusinessSettingsForm(instance=config)
    
    return render(request, 'config/config.html', {
        'config': config,
        'company_form': company_form,
        'financial_form': financial_form,
        'localization_form': localization_form,
        'business_form': business_form,
    })


@login_required
def get_config(request):
    """Get configuration via AJAX"""
    config = AppConfig.get_instance()
    
    data = {
        'company_name': config.company_name,
        'company_slogan': config.company_slogan,
        'phone': config.phone,
        'email': config.email,
        'address': config.address,
        'currency': config.currency,
        'tax_rate': float(config.tax_rate),
        'discount_rate': float(config.discount_rate),
        'invoice_prefix': config.invoice_prefix,
        'invoice_start_number': config.invoice_start_number,
        'invoice_footer_text': config.invoice_footer_text,
        'logo_url': config.logo.url if config.logo else None,
        'default_language': config.default_language,
        'timezone': config.timezone,
        'credit_enabled': config.credit_enabled,
        'max_credit_days': config.max_credit_days,
        'low_stock_threshold': config.low_stock_threshold,
        'maintenance_mode': config.maintenance_mode,
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_admin)
def update_config(request):
    """Update configuration via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    config = AppConfig.get_instance()
    
    # Update fields from POST data
    fields = [
        'company_name', 'company_slogan', 'phone', 'email', 'address',
        'currency', 'tax_rate', 'discount_rate', 'invoice_prefix',
        'invoice_start_number', 'invoice_footer_text', 'default_language',
        'timezone', 'credit_enabled', 'max_credit_days', 'low_stock_threshold',
        'maintenance_mode'
    ]
    
    for field in fields:
        if field in request.POST:
            value = request.POST[field]
            if field in ['tax_rate', 'discount_rate']:
                value = float(value) if value else 0.0
            elif field in ['invoice_start_number', 'max_credit_days', 'low_stock_threshold']:
                value = int(value) if value else 0
            elif field in ['credit_enabled', 'maintenance_mode']:
                value = value.lower() == 'true'
            setattr(config, field, value)
    
    config.save()
    
    return JsonResponse({'message': 'Configuration updated successfully'})
