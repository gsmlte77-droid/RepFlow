"""
Billing models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from repairs.models import RepairTicket
from clients.models import Client
from accounts.models import User
from config.models import AppConfig


class Invoice(models.Model):
    """Invoice model"""
    
    class InvoiceType(models.TextChoices):
        REPAIR = 'REPAIR', _('Repair')
        SALE = 'SALE', _('Sale')
        SERVICE = 'SERVICE', _('Service')
        QUOTATION = 'QUOTATION', _('Quotation')
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        PAID = 'PAID', _('Paid')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partially Paid')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REFUNDED = 'REFUNDED', _('Refunded')
    
    # Invoice Information
    invoice_number = models.CharField(
        _('Invoice Number'),
        max_length=50,
        unique=True
    )
    
    repair_ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.SET_NULL,
        related_name='invoices',
        blank=True,
        null=True,
        verbose_name=_('Repair Ticket')
    )
    
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name=_('Client')
    )
    
    invoice_type = models.CharField(
        _('Invoice Type'),
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.REPAIR
    )
    
    invoice_date = models.DateField(
        _('Invoice Date'),
        default=models.DateField(auto_now_add=True)
    )
    
    due_date = models.DateField(
        _('Due Date'),
        blank=True,
        null=True
    )
    
    reference = models.CharField(
        _('Reference'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Financial Information
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    tax_rate = models.DecimalField(
        _('Tax Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    tax_amount = models.DecimalField(
        _('Tax Amount'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    discount = models.DecimalField(
        _('Discount'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    total = models.DecimalField(
        _('Total'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    amount_paid = models.DecimalField(
        _('Amount Paid'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    balance_due = models.DecimalField(
        _('Balance Due'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    statut = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Credit Information
    statut_credit = models.CharField(
        _('Credit Status'),
        max_length=20,
        choices=[
            ('SOLDE', _('Settled')),
            ('EN_COURS', _('In Progress')),
        ],
        default='SOLDE'
    )
    
    reste_a_payer = models.DecimalField(
        _('Remaining to Pay'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    # Payment Terms
    payment_terms = models.TextField(
        _('Payment Terms'),
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    internal_notes = models.TextField(
        _('Internal Notes'),
        blank=True,
        null=True
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
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_invoices',
        blank=True,
        null=True
    )
    
    sent_date = models.DateTimeField(
        _('Sent Date'),
        blank=True,
        null=True
    )
    
    paid_date = models.DateTimeField(
        _('Paid Date'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-invoice_date', '-date_created']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['client']),
            models.Index(fields=['repair_ticket']),
            models.Index(fields=['statut']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client.get_display_name()}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate totals"""
        if not self.invoice_number:
            # Generate invoice number
            config = AppConfig.get_instance()
            
            # Get next invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[-1])
                    self.invoice_number = f"{config.invoice_prefix}-{last_num + 1:06d}"
                except:
                    self.invoice_number = f"{config.invoice_prefix}-000001"
            else:
                self.invoice_number = f"{config.invoice_prefix}-000001"
        
        # Calculate tax amount
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        
        # Calculate total
        self.total = self.subtotal + self.tax_amount - self.discount
        
        # Calculate balance due
        self.balance_due = self.total - self.amount_paid
        
        # Calculate remaining to pay (for credit)
        self.reste_a_payer = self.balance_due
        
        # Update credit status
        if self.balance_due <= 0:
            self.statut_credit = 'SOLDE'
        else:
            self.statut_credit = 'EN_COURS'
        
        # Update status based on balance
        if self.balance_due <= 0 and self.total > 0:
            self.statut = self.Status.PAID
            if not self.paid_date:
                self.paid_date = self.date_updated
        elif self.amount_paid > 0 and self.balance_due > 0:
            self.statut = self.Status.PARTIALLY_PAID
        elif self.statut == self.Status.DRAFT and self.total > 0:
            self.statut = self.Status.PENDING
        
        super().save(*args, **kwargs)
    
    def get_status_display_with_color(self):
        """Get status display with color class"""
        status_colors = {
            self.Status.DRAFT: 'bg-gray-100 text-gray-800',
            self.Status.PENDING: 'bg-blue-100 text-blue-800',
            self.Status.SENT: 'bg-yellow-100 text-yellow-800',
            self.Status.PAID: 'bg-green-100 text-green-800',
            self.Status.PARTIALLY_PAID: 'bg-orange-100 text-orange-800',
            self.Status.CANCELLED: 'bg-red-100 text-red-800',
            self.Status.REFUNDED: 'bg-purple-100 text-purple-800',
        }
        color = status_colors.get(self.statut, 'bg-gray-100 text-gray-800')
        return f"{self.get_statut_display()} ({color})"
    
    def is_paid(self):
        """Check if invoice is fully paid"""
        return self.balance_due <= 0
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        if self.due_date and self.balance_due > 0:
            return self.due_date < timezone.now().date()
        return False
    
    def get_days_overdue(self):
        """Get number of days overdue"""
        from django.utils import timezone
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0


class InvoiceItem(models.Model):
    """Items on an invoice"""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='invoice_items'
    )
    
    description = models.CharField(
        _('Description'),
        max_length=500
    )
    
    quantity = models.DecimalField(
        _('Quantity'),
        max_digits=8,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.01)]
    )
    
    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    tax_rate = models.DecimalField(
        _('Tax Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    total = models.DecimalField(
        _('Total'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    order = models.PositiveIntegerField(
        _('Order'),
        default=0
    )
    
    class Meta:
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate total"""
        self.total = (self.quantity * self.unit_price) * (1 + self.tax_rate / 100)
        
        # Update invoice subtotal
        if self.pk:
            old_item = InvoiceItem.objects.get(pk=self.pk)
            old_total = old_item.total
        else:
            old_total = 0
        
        super().save(*args, **kwargs)
        
        # Update invoice
        self.invoice.subtotal = sum(item.total for item in self.invoice.invoice_items.all())
        self.invoice.save()


class Payment(models.Model):
    """Payment model"""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', _('Cash')
        CARD = 'CARD', _('Credit/Debit Card')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CHECK = 'CHECK', _('Check')
        MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
        ONLINE = 'ONLINE', _('Online Payment')
        OTHER = 'OTHER', _('Other')
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Invoice')
    )
    
    amount = models.DecimalField(
        _('Amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    
    reference = models.CharField(
        _('Reference'),
        max_length=100,
        blank=True,
        null=True
    )
    
    transaction_date = models.DateTimeField(
        _('Transaction Date'),
        auto_now_add=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='payments_created',
        blank=True,
        null=True
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
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.get_payment_method_display()} - {self.amount} - {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        """Override save to update invoice"""
        if not self.pk:
            # New payment
            old_amount_paid = self.invoice.amount_paid
        else:
            old_payment = Payment.objects.get(pk=self.pk)
            old_amount_paid = old_payment.amount
        
        super().save(*args, **kwargs)
        
        # Update invoice
        self.invoice.amount_paid = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.save()


# Signals
@receiver(post_save, sender=RepairTicket)
def create_invoice_from_repair(sender, instance, created, **kwargs):
    """Automatically create an invoice when repair ticket is completed"""
    if created:
        # Create draft invoice
        Invoice.objects.create(
            repair_ticket=instance,
            client=instance.client,
            invoice_type=Invoice.InvoiceType.REPAIR,
            statut=Invoice.Status.DRAFT,
            subtotal=instance.cout_total,
            tax_rate=instance.client.discount_rate,
            discount=instance.discount,
            created_by=instance.created_by
        )
    elif instance.statut == RepairTicket.Status.READY:
        # Check if invoice exists
        invoice, created = Invoice.objects.get_or_create(
            repair_ticket=instance,
            defaults={
                'client': instance.client,
                'invoice_type': Invoice.InvoiceType.REPAIR,
                'statut': Invoice.Status.PENDING,
                'subtotal': instance.cout_total,
                'tax_rate': instance.client.discount_rate,
                'discount': instance.discount,
                'created_by': instance.created_by
            }
        )
        
        if not created:
            # Update existing invoice
            invoice.subtotal = instance.cout_total
            invoice.tax_rate = instance.client.discount_rate
            invoice.discount = instance.discount
            invoice.save()
