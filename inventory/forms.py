"""
Inventory forms for FixSoftRepair
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import InventoryItem, Category, Supplier, StockMovement


class CategoryForm(forms.ModelForm):
    """Category form"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }


class SupplierForm(forms.ModelForm):
    """Supplier form"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'telephone', 'email', 'address',
            'website', 'tax_id', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }


class InventoryItemForm(forms.ModelForm):
    """Inventory item form"""
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'reference_sku', 'barcode', 'item_type',
            'category', 'supplier', 'quantite_stock', 'seuil_alerte', 'location',
            'prix_achat', 'prix_vente', 'weight', 'dimensions', 'warranty_period',
            'minimum_order_quantity', 'is_active', 'is_taxable', 'is_serialized'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'reference_sku': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'item_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'quantite_stock': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'seuil_alerte': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'prix_achat': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'prix_vente': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.001',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'warranty_period': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'minimum_order_quantity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'is_taxable': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
            'is_serialized': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            }),
        }


class InventorySearchForm(forms.Form):
    """Inventory search form"""
    
    search = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': _('Search by name, SKU, or barcode...')
        })
    )
    
    category = forms.ModelChoiceField(
        label=_('Category'),
        required=False,
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    supplier = forms.ModelChoiceField(
        label=_('Supplier'),
        required=False,
        queryset=Supplier.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    item_type = forms.ChoiceField(
        label=_('Item Type'),
        required=False,
        choices=[('', _('All Types'))] + list(InventoryItem.ItemType.choices),
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    stock_status = forms.ChoiceField(
        label=_('Stock Status'),
        required=False,
        choices=[
            ('', _('All Statuses')),
            ('IN_STOCK', _('In Stock')),
            ('LOW_STOCK', _('Low Stock')),
            ('OUT_OF_STOCK', _('Out of Stock')),
        ],
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


class StockAdjustmentForm(forms.ModelForm):
    """Stock adjustment form"""
    
    class Meta:
        model = StockMovement
        fields = ['item', 'movement_type', 'quantity', 'reference', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }


class QuickStockForm(forms.Form):
    """Quick stock adjustment form"""
    
    item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        label=_('Quantity'),
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
            'min': '1'
        })
    )
    operation = forms.ChoiceField(
        label=_('Operation'),
        choices=[
            ('add', _('Add to Stock')),
            ('subtract', _('Subtract from Stock')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    notes = forms.CharField(
        label=_('Notes'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
