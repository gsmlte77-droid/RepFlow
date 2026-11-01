"""
Repairs models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from clients.models import Client
from accounts.models import User
from inventory.models import InventoryItem
from config.models import AppConfig


class RepairTicket(models.Model):
    """Repair ticket model"""
    
    class DeviceType(models.TextChoices):
        MOBILE = 'MOBILE', _('Mobile Phone')
        TABLET = 'TABLET', _('Tablet')
        LAPTOP = 'LAPTOP', _('Laptop')
        DESKTOP = 'DESKTOP', _('Desktop Computer')
        AUTO = 'AUTO', _('Automobile')
        MOTORCYCLE = 'MOTORCYCLE', _('Motorcycle')
        ELECTRONIC = 'ELECTRONIC', _('Electronic Device')
        APPLIANCE = 'APPLIANCE', _('Home Appliance')
        MOTOR = 'MOTOR', _('Motor/Engine')
        OTHER = 'OTHER', _('Other')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        DIAGNOSIS = 'DIAGNOSIS', _('Diagnosis')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        WAITING_PARTS = 'WAITING_PARTS', _('Waiting for Parts')
        QUOTATION = 'QUOTATION', _('Quotation Sent')
        READY = 'READY', _('Ready for Delivery')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REJECTED = 'REJECTED', _('Rejected')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        NORMAL = 'NORMAL', _('Normal')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    # Ticket Information
    ticket_number = models.CharField(
        _('Ticket Number'),
        max_length=50,
        unique=True
    )
    
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='repair_tickets',
        verbose_name=_('Client')
    )
    
    # Device Information
    appareil = models.CharField(
        _('Device Name'),
        max_length=200
    )
    
    type_appareil = models.CharField(
        _('Device Type'),
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.MOBILE
    )
    
    brand = models.CharField(
        _('Brand'),
        max_length=100,
        blank=True,
        null=True
    )
    
    model = models.CharField(
        _('Model'),
        max_length=100,
        blank=True,
        null=True
    )
    
    serial_number = models.CharField(
        _('Serial Number'),
        max_length=100,
        blank=True,
        null=True
    )
    
    device_condition = models.CharField(
        _('Device Condition'),
        max_length=200,
        blank=True,
        null=True
    )
    
    # Repair Information
    description_panne = models.TextField(
        _('Problem Description'),
        blank=True,
        null=True
    )
    
    diagnosis = models.TextField(
        _('Diagnosis'),
        blank=True,
        null=True
    )
    
    repair_notes = models.TextField(
        _('Repair Notes'),
        blank=True,
        null=True
    )
    
    internal_notes = models.TextField(
        _('Internal Notes'),
        blank=True,
        null=True
    )
    
    # Assignment
    technicien = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_repairs',
        blank=True,
        null=True,
        verbose_name=_('Technician')
    )
    
    # Status and Priority
    statut = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    priority = models.CharField(
        _('Priority'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    
    # Financial Information
    cout_main_oeuvre = models.DecimalField(
        _('Labor Cost'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    cout_pieces = models.DecimalField(
        _('Parts Cost'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    cout_total = models.DecimalField(
        _('Total Cost'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    discount = models.DecimalField(
        _('Discount'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    amount_paid = models.DecimalField(
        _('Amount Paid'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    # Dates
    date_depot = models.DateTimeField(
        _('Deposit Date'),
        auto_now_add=True
    )
    
    date_restitution_prevue = models.DateField(
        _('Expected Delivery Date'),
        blank=True,
        null=True
    )
    
    date_restitution = models.DateTimeField(
        _('Actual Delivery Date'),
        blank=True,
        null=True
    )
    
    date_completed = models.DateTimeField(
        _('Completion Date'),
        blank=True,
        null=True
    )
    
    # Warranty
    warranty_months = models.PositiveIntegerField(
        _('Warranty Months'),
        default=0,
        help_text=_('Warranty period for this repair')
    )
    
    warranty_notes = models.TextField(
        _('Warranty Notes'),
        blank=True,
        null=True
    )
    
    # Additional Information
    accessories = models.TextField(
        _('Accessories'),
        blank=True,
        null=True,
        help_text=_('List of accessories received with the device')
    )
    
    password = models.CharField(
        _('Device Password'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Status Flags
    is_under_warranty = models.BooleanField(
        _('Under Warranty'),
        default=False
    )
    
    is_insured = models.BooleanField(
        _('Insured'),
        default=False
    )
    
    requires_approval = models.BooleanField(
        _('Requires Approval'),
        default=False
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='approved_repairs',
        blank=True,
        null=True
    )
    
    approved_date = models.DateTimeField(
        _('Approval Date'),
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
        related_name='created_repairs',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Repair Ticket')
        verbose_name_plural = _('Repair Tickets')
        ordering = ['-date_depot']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['client']),
            models.Index(fields=['technicien']),
            models.Index(fields=['statut']),
            models.Index(fields=['date_depot']),
            models.Index(fields=['date_restitution_prevue']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.appareil}"
    
    def save(self, *args, **kwargs):
        """Override save to update total cost"""
        if not self.ticket_number:
            # Generate ticket number
            from config.models import AppConfig
            config = AppConfig.get_instance()
            
            # Get next ticket number
            last_ticket = RepairTicket.objects.order_by('-id').first()
            if last_ticket:
                try:
                    last_num = int(last_ticket.ticket_number.split('-')[-1])
                    self.ticket_number = f"{config.invoice_prefix}-{last_num + 1:06d}"
                except:
                    self.ticket_number = f"{config.invoice_prefix}-000001"
            else:
                self.ticket_number = f"{config.invoice_prefix}-000001"
        
        # Calculate total cost
        self.cout_total = self.cout_main_oeuvre + self.cout_pieces - self.discount
        
        # Update status timestamps
        if self.statut == self.Status.COMPLETED and not self.date_completed:
            self.date_completed = self.date_updated
        
        if self.statut == self.Status.DELIVERED and not self.date_restitution:
            self.date_restitution = self.date_updated
        
        super().save(*args, **kwargs)
    
    def get_status_display_with_color(self):
        """Get status display with color class"""
        status_colors = {
            self.Status.PENDING: 'bg-gray-100 text-gray-800',
            self.Status.DIAGNOSIS: 'bg-blue-100 text-blue-800',
            self.Status.IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
            self.Status.WAITING_PARTS: 'bg-orange-100 text-orange-800',
            self.Status.QUOTATION: 'bg-purple-100 text-purple-800',
            self.Status.READY: 'bg-green-100 text-green-800',
            self.Status.DELIVERED: 'bg-emerald-100 text-emerald-800',
            self.Status.CANCELLED: 'bg-red-100 text-red-800',
            self.Status.REJECTED: 'bg-red-200 text-red-900',
        }
        color = status_colors.get(self.statut, 'bg-gray-100 text-gray-800')
        return f"{self.get_statut_display()} ({color})"
    
    def get_priority_display_with_color(self):
        """Get priority display with color class"""
        priority_colors = {
            self.Priority.LOW: 'bg-gray-100 text-gray-800',
            self.Priority.NORMAL: 'bg-blue-100 text-blue-800',
            self.Priority.HIGH: 'bg-orange-100 text-orange-800',
            self.Priority.URGENT: 'bg-red-100 text-red-800',
        }
        color = priority_colors.get(self.priority, 'bg-gray-100 text-gray-800')
        return f"{self.get_priority_display()} ({color})"
    
    def get_balance_due(self):
        """Calculate remaining balance"""
        return self.cout_total - self.amount_paid
    
    def is_paid(self):
        """Check if ticket is fully paid"""
        return self.get_balance_due() <= 0
    
    def is_overdue(self):
        """Check if ticket is overdue"""
        from django.utils import timezone
        if self.date_restitution_prevue:
            return self.date_restitution_prevue < timezone.now().date() and self.statut != self.Status.DELIVERED
        return False
    
    def get_device_info(self):
        """Get formatted device information"""
        parts = [self.appareil]
        if self.brand:
            parts.append(self.brand)
        if self.model:
            parts.append(self.model)
        if self.serial_number:
            parts.append(f"SN: {self.serial_number}")
        return " - ".join(parts)


class RepairPart(models.Model):
    """Parts used in repair"""
    
    repair_ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='repair_parts',
        verbose_name=_('Repair Ticket')
    )
    
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        related_name='repair_parts',
        blank=True,
        null=True,
        verbose_name=_('Inventory Item')
    )
    
    name = models.CharField(
        _('Part Name'),
        max_length=200
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    total_price = models.DecimalField(
        _('Total Price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    serial_number = models.CharField(
        _('Serial Number'),
        max_length=100,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    date_added = models.DateTimeField(
        _('Date Added'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Repair Part')
        verbose_name_plural = _('Repair Parts')
        ordering = ['-date_added']
    
    def __str__(self):
        return f"{self.name} - {self.repair_ticket.ticket_number}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate total price"""
        self.total_price = self.quantity * self.unit_price
        
        # Update repair ticket parts cost
        if self.pk:
            # Existing part, need to recalculate
            old_part = RepairPart.objects.get(pk=self.pk)
            old_total = old_part.total_price
        else:
            old_total = 0
        
        super().save(*args, **kwargs)
        
        # Update repair ticket
        self.repair_ticket.cout_pieces = sum(
            part.total_price for part in self.repair_ticket.repair_parts.all()
        )
        self.repair_ticket.cout_total = self.repair_ticket.cout_main_oeuvre + self.repair_ticket.cout_pieces - self.repair_ticket.discount
        self.repair_ticket.save()
    
    def delete(self, *args, **kwargs):
        """Override delete to update repair ticket"""
        # Update repair ticket
        self.repair_ticket.cout_pieces = sum(
            part.total_price for part in self.repair_ticket.repair_parts.all() if part.pk != self.pk
        )
        self.repair_ticket.cout_total = self.repair_ticket.cout_main_oeuvre + self.repair_ticket.cout_pieces - self.repair_ticket.discount
        self.repair_ticket.save()
        
        super().delete(*args, **kwargs)


class RepairHistory(models.Model):
    """Repair ticket history"""
    
    class Action(models.TextChoices):
        CREATED = 'CREATED', _('Created')
        UPDATED = 'UPDATED', _('Updated')
        STATUS_CHANGED = 'STATUS_CHANGED', _('Status Changed')
        ASSIGNED = 'ASSIGNED', _('Assigned')
        DIAGNOSIS_ADDED = 'DIAGNOSIS_ADDED', _('Diagnosis Added')
        PART_ADDED = 'PART_ADDED', _('Part Added')
        PART_REMOVED = 'PART_REMOVED', _('Part Removed')
        COMPLETED = 'COMPLETED', _('Completed')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    repair_ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Repair Ticket')
    )
    
    action = models.CharField(
        _('Action'),
        max_length=50,
        choices=Action.choices
    )
    
    old_value = models.TextField(
        _('Old Value'),
        blank=True,
        null=True
    )
    
    new_value = models.TextField(
        _('New Value'),
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='repair_history',
        blank=True,
        null=True
    )
    
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Repair History')
        verbose_name_plural = _('Repair History')
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.repair_ticket.ticket_number}"


# Signals to track repair ticket changes
@receiver(post_save, sender=RepairTicket)
def track_repair_ticket_changes(sender, instance, created, **kwargs):
    """Track changes to repair tickets"""
    if created:
        RepairHistory.objects.create(
            repair_ticket=instance,
            action=RepairHistory.Action.CREATED,
            new_value=str(instance),
            created_by=instance.created_by
        )
    else:
        # Check for status changes
        if instance.pk:
            try:
                old_ticket = RepairTicket.objects.get(pk=instance.pk)
                if old_ticket.statut != instance.statut:
                    RepairHistory.objects.create(
                        repair_ticket=instance,
                        action=RepairHistory.Action.STATUS_CHANGED,
                        old_value=old_ticket.get_statut_display(),
                        new_value=instance.get_statut_display(),
                        created_by=instance.updated_by if hasattr(instance, 'updated_by') else None
                    )
            except RepairTicket.DoesNotExist:
                pass


@receiver(post_save, sender=RepairPart)
def track_repair_part_added(sender, instance, created, **kwargs):
    """Track when parts are added to repairs"""
    if created:
        RepairHistory.objects.create(
            repair_ticket=instance.repair_ticket,
            action=RepairHistory.Action.PART_ADDED,
            new_value=f"{instance.name} ({instance.quantity} x {instance.unit_price})",
            created_by=instance.repair_ticket.updated_by if hasattr(instance.repair_ticket, 'updated_by') else None
        )


@receiver(post_delete, sender=RepairPart)
def track_repair_part_removed(sender, instance, **kwargs):
    """Track when parts are removed from repairs"""
    RepairHistory.objects.create(
        repair_ticket=instance.repair_ticket,
        action=RepairHistory.Action.PART_REMOVED,
        old_value=f"{instance.name} ({instance.quantity} x {instance.unit_price})",
        created_by=instance.repair_ticket.updated_by if hasattr(instance.repair_ticket, 'updated_by') else None
    )
