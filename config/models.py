"""
Config models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class AppConfig(models.Model):
    """
    Singleton model for global application configuration
    Only one instance should exist in the database
    """
    
    class Currency(models.TextChoices):
        USD = 'USD', _('US Dollar')
        EUR = 'EUR', _('Euro')
        GBP = 'GBP', _('British Pound')
        DZD = 'DZD', _('Algerian Dinar')
        MAD = 'MAD', _('Moroccan Dirham')
        TND = 'TND', _('Tunisian Dinar')
        SAR = 'SAR', _('Saudi Riyal')
        AED = 'AED', _('UAE Dirham')
        QAR = 'QAR', _('Qatari Riyal')
    
    class Language(models.TextChoices):
        FR = 'fr', _('French')
        EN = 'en', _('English')
        AR = 'ar', _('Arabic')
    
    # Company Information
    company_name = models.CharField(
        _('Company Name'),
        max_length=200,
        default='FixSoftRepair'
    )
    
    company_slogan = models.CharField(
        _('Company Slogan'),
        max_length=500,
        blank=True,
        null=True
    )
    
    phone = models.CharField(
        _('Phone'),
        max_length=50,
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        _('Email'),
        blank=True,
        null=True
    )
    
    website = models.URLField(
        _('Website'),
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('Address'),
        blank=True,
        null=True
    )
    
    city = models.CharField(
        _('City'),
        max_length=100,
        blank=True,
        null=True
    )
    
    postal_code = models.CharField(
        _('Postal Code'),
        max_length=20,
        blank=True,
        null=True
    )
    
    country = models.CharField(
        _('Country'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Financial Settings
    currency = models.CharField(
        _('Currency'),
        max_length=3,
        choices=Currency.choices,
        default=Currency.DZD
    )
    
    tax_rate = models.DecimalField(
        _('Tax Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=19.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Default tax rate in percentage')
    )
    
    discount_rate = models.DecimalField(
        _('Default Discount Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Invoice Settings
    invoice_prefix = models.CharField(
        _('Invoice Prefix'),
        max_length=20,
        default='INV'
    )
    
    invoice_start_number = models.PositiveIntegerField(
        _('Invoice Start Number'),
        default=1
    )
    
    invoice_footer_text = models.TextField(
        _('Invoice Footer Text'),
        blank=True,
        null=True,
        help_text=_('Text to appear at the bottom of invoices')
    )
    
    invoice_terms = models.TextField(
        _('Invoice Terms and Conditions'),
        blank=True,
        null=True
    )
    
    # Branding
    logo = models.ImageField(
        _('Logo'),
        upload_to='config/',
        blank=True,
        null=True
    )
    
    favicon = models.ImageField(
        _('Favicon'),
        upload_to='config/',
        blank=True,
        null=True
    )
    
    # Localization
    default_language = models.CharField(
        _('Default Language'),
        max_length=10,
        choices=Language.choices,
        default=Language.FR
    )
    
    timezone = models.CharField(
        _('Timezone'),
        max_length=50,
        default='Africa/Algiers'
    )
    
    date_format = models.CharField(
        _('Date Format'),
        max_length=20,
        default='Y-m-d'
    )
    
    # Business Settings
    business_hours = models.TextField(
        _('Business Hours'),
        blank=True,
        null=True,
        help_text=_('Description of business hours')
    )
    
    max_credit_days = models.PositiveIntegerField(
        _('Maximum Credit Days'),
        default=30,
        help_text=_('Maximum number of days for credit payments')
    )
    
    credit_enabled = models.BooleanField(
        _('Enable Credit Sales'),
        default=True
    )
    
    # Notification Settings
    low_stock_threshold = models.PositiveIntegerField(
        _('Low Stock Threshold'),
        default=5,
        help_text=_('Alert when stock quantity falls below this number')
    )
    
    email_notifications = models.BooleanField(
        _('Email Notifications'),
        default=True
    )
    
    sms_notifications = models.BooleanField(
        _('SMS Notifications'),
        default=False
    )
    
    # System Settings
    system_name = models.CharField(
        _('System Name'),
        max_length=100,
        default='FixSoftRepair'
    )
    
    version = models.CharField(
        _('Version'),
        max_length=20,
        default='1.0.0'
    )
    
    maintenance_mode = models.BooleanField(
        _('Maintenance Mode'),
        default=False,
        help_text=_('Enable maintenance mode to prevent new repairs')
    )
    
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    date_updated = models.DateTimeField(
        _('Date Updated'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Application Configuration')
        verbose_name_plural = _('Application Configurations')
    
    def __str__(self):
        return f"{self.company_name} Configuration"
    
    def clean(self):
        """Ensure only one instance exists"""
        if self.pk:
            # If updating, make sure we're not creating a second instance
            if AppConfig.objects.exclude(pk=self.pk).exists():
                raise ValidationError(_('Only one configuration instance is allowed.'))
        else:
            # If creating, check if one already exists
            if AppConfig.objects.exists():
                raise ValidationError(_('Only one configuration instance is allowed.'))
    
    def save(self, *args, **kwargs):
        """Override save to ensure singleton pattern"""
        self.full_clean()
        super().save(*args, **kwargs)
        # Clear cache
        from django.core.cache import cache
        cache.delete('app_config')
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance"""
        raise ValidationError(_('Cannot delete the configuration instance.'))
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance, create if doesn't exist"""
        from django.core.cache import cache
        
        config = cache.get('app_config')
        if config is None:
            config, created = cls.objects.get_or_create(
                defaults={
                    'company_name': 'FixSoftRepair',
                    'currency': cls.Currency.DZD,
                    'tax_rate': 19.00,
                    'default_language': cls.Language.FR,
                    'timezone': 'Africa/Algiers'
                }
            )
            cache.set('app_config', config, timeout=3600)  # Cache for 1 hour
        
        return config
