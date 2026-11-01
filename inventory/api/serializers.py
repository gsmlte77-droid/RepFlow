"""
Inventory API serializers
"""
from rest_framework import serializers
from ..models import InventoryItem, Category, Supplier, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'is_active', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']


class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'telephone', 'email', 'address',
            'website', 'tax_id', 'notes', 'is_active', 'date_created', 'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Inventory item serializer"""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'reference_sku', 'barcode', 'item_type',
            'category', 'category_id', 'supplier', 'supplier_id',
            'quantite_stock', 'seuil_alerte', 'location', 'prix_achat', 'prix_vente',
            'weight', 'dimensions', 'warranty_period', 'minimum_order_quantity',
            'is_active', 'is_taxable', 'is_serialized', 'date_created', 'date_updated',
            'last_restock_date', 'stock_status', 'profit_margin', 'total_value'
        ]
        read_only_fields = ['date_created', 'date_updated', 'stock_status', 'profit_margin', 'total_value']
    
    def get_stock_status(self, obj):
        return obj.get_stock_status()
    
    def get_profit_margin(self, obj):
        return float(obj.get_profit_margin())
    
    def get_total_value(self, obj):
        return float(obj.get_total_value())


class InventoryItemListSerializer(serializers.ModelSerializer):
    """Simplified inventory item serializer for lists"""
    
    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'reference_sku', 'barcode', 'item_type',
            'category', 'supplier', 'quantite_stock', 'seuil_alerte',
            'prix_achat', 'prix_vente', 'is_active', 'stock_status'
        ]
    
    def get_stock_status(self, obj):
        return obj.get_stock_status()


class InventoryItemSimpleSerializer(serializers.ModelSerializer):
    """Minimal inventory item serializer for dropdowns"""
    
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'reference_sku', 'quantite_stock', 'prix_vente']
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'reference_sku': instance.reference_sku,
            'barcode': instance.barcode,
            'stock': instance.quantite_stock,
            'price': float(instance.prix_vente),
            'can_be_sold': instance.can_be_sold()
        }


class StockMovementSerializer(serializers.ModelSerializer):
    """Stock movement serializer"""
    
    item = InventoryItemSimpleSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItem.objects.all(),
        source='item',
        write_only=True
    )
    
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_id', 'movement_type', 'quantity',
            'quantity_before', 'quantity_after', 'reference', 'notes',
            'created_by', 'date_created'
        ]
        read_only_fields = ['quantity_before', 'quantity_after', 'created_by', 'date_created']
