"""
Clients models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator


class Client(models.Model):
    """Client model with detailed information"""
    
    class ClientType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        BUSINESS = 'BUSINESS', _('Business')
        CORPORATE = 'CORPORATE', _('Corporate')
        GOVERNMENT = 'GOVERNMENT', _('Government')
    
    class MembershipStatus(models.TextChoices):
        STANDARD = 'STANDARD', _('Standard')
        PREMIUM = 'PREMIUM', _('Premium')
        VIP = 'VIP', _('VIP')
    
    # Basic Information
    first_name = models.CharField(
        _('First Name'),
        max_length=100
    )
    
    last_name = models.CharField(
        _('Last Name'),
        max_length=100,
        blank=True,
        null=True
    )
    
    company_name = models.CharField(
        _('Company Name'),
        max_length=200,
        blank=True,
        null=True
    )
    
    client_type = models.CharField(
        _('Client Type'),
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL
    )
    
    # Contact Information
    telephone = models.CharField(
        _('Telephone'),
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        ]
    )
    
    secondary_telephone = models.CharField(
        _('Secondary Telephone'),
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        ]
    )
    
    email = models.EmailField(
        _('Email'),
        blank=True,
        null=True,
        validators=[EmailValidator()]
    )
    
    secondary_email = models.EmailField(
        _('Secondary Email'),
        blank=True,
        null=True,
        validators=[EmailValidator()]
    )
    
    # Address Information
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
    
    state = models.CharField(
        _('State/Province'),
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
    
    # Business Information
    tax_id = models.CharField(
        _('Tax ID'),
        max_length=50,
        blank=True,
        null=True
    )
    
    registration_number = models.CharField(
        _('Registration Number'),
        max_length=50,
        blank=True,
        null=True
    )
    
    # Financial Information
    credit_limit = models.DecimalField(
        _('Credit Limit'),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Maximum credit allowed for this client')
    )
    
    current_balance = models.DecimalField(
        _('Current Balance'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_('Current outstanding balance')
    )
    
    membership_status = models.CharField(
        _('Membership Status'),
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.STANDARD
    )
    
    discount_rate = models.DecimalField(
        _('Discount Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Default discount rate for this client')
    )
    
    # Marketing Information
    referral_source = models.CharField(
        _('Referral Source'),
        max_length=100,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(
        _('Active'),
        default=True
    )
    
    is_blacklisted = models.BooleanField(
        _('Blacklisted'),
        default=False,
        help_text=_('Mark as blacklisted to prevent new repairs')
    )
    
    # Timestamps
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    date_updated = models.DateTimeField(
        _('Date Updated'),
        auto_now=True
    )
    
    last_contact_date = models.DateField(
        _('Last Contact Date'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['telephone']),
            models.Index(fields=['email']),
            models.Index(fields=['client_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.get_full_name()})"
        return self.get_full_name()
    
    def get_full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def get_display_name(self):
        if self.company_name:
            return self.company_name
        return self.get_full_name()
    
    def get_contact_info(self):
        contacts = []
        if self.telephone:
            contacts.append(f"Tel: {self.telephone}")
        if self.secondary_telephone:
            contacts.append(f"Tel2: {self.secondary_telephone}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        return ", ".join(contacts)
    
    def get_address(self):
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else None
    
    def get_balance_status(self):
        if self.current_balance > 0:
            return _('Owes: {}').format(self.current_balance)
        elif self.current_balance < 0:
            return _('Credit: {}').format(abs(self.current_balance))
        return _('Balanced')
    
    def can_receive_credit(self):
        """Check if client can receive credit"""
        if self.is_blacklisted:
            return False
        if not self.is_active:
            return False
        if self.credit_limit is None:
            return True
        return self.current_balance < self.credit_limit
