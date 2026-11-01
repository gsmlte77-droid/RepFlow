"""
Context processors for FixSoftRepair configuration
"""
from .models import AppConfig


def app_config(request):
    """
    Add app configuration to template context
    """
    try:
        config = AppConfig.get_instance()
    except Exception:
        config = None
    
    return {
        'app_config': config,
        'company_name': config.company_name if config else 'FixSoftRepair',
        'company_currency': config.currency if config else 'DZD',
        'company_tax_rate': config.tax_rate if config else 19.00,
        'company_logo': config.logo if config else None,
    }
