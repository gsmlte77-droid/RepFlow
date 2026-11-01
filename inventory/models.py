"""
Inventory models for FixSoftRepair
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from config.models import AppConfig


class Category(models.Model):
    """Category model for inventory items"""
    
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True
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
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_full_name(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.get_full_name()} > {self.name}"
        return self.name


class Supplier(models.Model):
    """Supplier model"""
    
    name = models.CharField(
        _('Name'),
        max_length=200
    )
    
    contact_person = models.CharField(
        _('Contact Person'),
        max_length=100,
        blank=True,
        null=True
    )
    
    telephone = models.CharField(
        _('Telephone'),
        max_length=20,
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        _('Email'),
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('Address'),
        blank=True,
        null=True
    )
    
    website = models.URLField(
        _('Website'),
        blank=True,
        null=True
    )
    
    tax_id = models.CharField(
        _('Tax ID'),
        max_length=50,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True
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
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Inventory item model"""
    
    class ItemType(models.TextChoices):
        PART = 'PART', _('Part')
        ACCESSORY = 'ACCESSORY', _('Accessory')
        CONSUMABLE = 'CONSUMABLE', _('Consumable')
        TOOL = 'TOOL', _('Tool')
        EQUIPMENT = 'EQUIPMENT', _('Equipment')
        OTHER = 'OTHER', _('Other')
    
    class StockStatus(models.TextChoices):
        IN_STOCK = 'IN_STOCK', _('In Stock')
        LOW_STOCK = 'LOW_STOCK', _('Low Stock')
        OUT_OF_STOCK = 'OUT_OF_STOCK', _('Out of Stock')
        DISCONTINUED = 'DISCONTINUED', _('Discontinued')
    
    # Basic Information
    name = models.CharField(
        _('Name'),
        max_length=200
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    
    reference_sku = models.CharField(
        _('SKU/Reference'),
        max_length=100,
        unique=True
    )
    
    barcode = models.CharField(
        _('Barcode'),
        max_length=100,
        blank=True,
        null=True
    )
    
    item_type = models.CharField(
        _('Item Type'),
        max_length=20,
        choices=ItemType.choices,
        default=ItemType.PART
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    
    # Stock Information
    quantite_stock = models.PositiveIntegerField(
        _('Quantity in Stock'),
        default=0
    )
    
    seuil_alerte = models.PositiveIntegerField(
        _('Alert Threshold'),
        default=5,
        validators=[MinValueValidator(0)]
    )
    
    location = models.CharField(
        _('Storage Location'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Financial Information
    prix_achat = models.DecimalField(
        _('Purchase Price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    prix_vente = models.DecimalField(
        _('Selling Price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    # Additional Information
    weight = models.DecimalField(
        _('Weight (kg)'),
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    dimensions = models.CharField(
        _('Dimensions'),
        max_length=100,
        blank=True,
        null=True
    )
    
    warranty_period = models.PositiveIntegerField(
        _('Warranty Period (months)'),
        blank=True,
        null=True
    )
    
    minimum_order_quantity = models.PositiveIntegerField(
        _('Minimum Order Quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    # Status
    is_active = models.BooleanField(
        _('Active'),
        default=True
    )
    
    is_taxable = models.BooleanField(
        _('Taxable'),
        default=True
    )
    
    is_serialized = models.BooleanField(
        _('Serialized'),
        default=False,
        help_text=_('Track individual serial numbers')
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
    
    last_restock_date = models.DateField(
        _('Last Restock Date'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Inventory Item')
        verbose_name_plural = _('Inventory Items')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['reference_sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
            models.Index(fields=['quantite_stock']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.reference_sku})"
    
    def get_stock_status(self):
        """Get stock status based on quantity and threshold"""
        config = AppConfig.get_instance()
        threshold = self.seuil_alerte if self.seuil_alerte > 0 else config.low_stock_threshold
        
        if not self.is_active:
            return self.StockStatus.DISCONTINUED
        elif self.quantite_stock == 0:
            return self.StockStatus.OUT_OF_STOCK
        elif self.quantite_stock <= threshold:
            return self.StockStatus.LOW_STOCK
        return self.StockStatus.IN_STOCK
    
    def get_stock_status_display(self):
        """Get display for stock status"""
        return self.get_stock_status().label
    
    def get_profit_margin(self):
        """Calculate profit margin"""
        if self.prix_achat > 0:
            return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100
        return 0.00
    
    def get_total_value(self):
        """Calculate total inventory value"""
        return self.quantite_stock * self.prix_achat
    
    def can_be_sold(self):
        """Check if item can be sold"""
        return self.is_active and self.quantite_stock > 0
    
    def update_stock(self, quantity, operation='add'):
        """
        Update stock quantity
        operation: 'add' to increase, 'subtract' to decrease
        """
        if operation == 'add':
            self.quantite_stock += quantity
        elif operation == 'subtract':
            if self.quantite_stock >= quantity:
                self.quantite_stock -= quantity
            else:
                raise ValueError(_('Insufficient stock'))
        self.save()
        return self.quantite_stock


class SerialNumber(models.Model):
    """Serial number tracking for inventory items"""
    
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='serial_numbers'
    )
    
    serial_number = models.CharField(
        _('Serial Number'),
        max_length=100,
        unique=True
    )
    
    purchase_date = models.DateField(
        _('Purchase Date'),
        blank=True,
        null=True
    )
    
    purchase_price = models.DecimalField(
        _('Purchase Price'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name='serial_numbers',
        blank=True,
        null=True
    )
    
    status = models.CharField(
        _('Status'),
        max_length=50,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    is_sold = models.BooleanField(
        _('Sold'),
        default=False
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
        verbose_name = _('Serial Number')
        verbose_name_plural = _('Serial Numbers')
        ordering = ['serial_number']
    
    def __str__(self):
        return f"{self.item.name} - {self.serial_number}"


class StockMovement(models.Model):
    """Stock movement history"""
    
    class MovementType(models.TextChoices):
        PURCHASE = 'PURCHASE', _('Purchase')
        SALE = 'SALE', _('Sale')
        RETURN = 'RETURN', _('Return')
        ADJUSTMENT = 'ADJUSTMENT', _('Adjustment')
        TRANSFER = 'TRANSFER', _('Transfer')
        DAMAGE = 'DAMAGE', _('Damage')
        OTHER = 'OTHER', _('Other')
    
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    
    movement_type = models.CharField(
        _('Movement Type'),
        max_length=20,
        choices=MovementType.choices
    )
    
    quantity = models.IntegerField(
        _('Quantity'),
        validators=[MinValueValidator(1)]
    )
    
    quantity_before = models.PositiveIntegerField(
        _('Quantity Before'),
        default=0
    )
    
    quantity_after = models.PositiveIntegerField(
        _('Quantity After'),
        default=0
    )
    
    reference = models.CharField(
        _('Reference'),
        max_length=100,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='stock_movements',
        blank=True,
        null=True
    )
    
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.item.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """Override save to update item stock"""
        if not self.pk:
            # New movement
            self.quantity_before = self.item.quantite_stock
            
            if self.movement_type in [self.MovementType.PURCHASE, self.MovementType.RETURN, self.MovementType.ADJUSTMENT]:
                self.item.quantite_stock += self.quantity
            elif self.movement_type in [self.MovementType.SALE, self.MovementType.TRANSFER, self.MovementType.DAMAGE]:
                if self.item.quantite_stock >= self.quantity:
                    self.item.quantite_stock -= self.quantity
                else:
                    raise ValueError(_('Insufficient stock'))
            
            self.quantity_after = self.item.quantite_stock
            self.item.save()
        
        super().save(*args, **kwargs)
