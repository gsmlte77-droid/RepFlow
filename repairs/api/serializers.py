"""
Repairs API serializers
"""
from rest_framework import serializers
from ..models import RepairTicket, RepairPart, RepairHistory
from clients.api.serializers import ClientSimpleSerializer
from accounts.api.serializers import UserSerializer
from inventory.api.serializers import InventoryItemSimpleSerializer


class RepairTicketSerializer(serializers.ModelSerializer):
    """Repair ticket serializer"""
    
    client = ClientSimpleSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    
    technicien = UserSerializer(read_only=True)
    technicien_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='technicien',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    created_by = UserSerializer(read_only=True)
    
    balance_due = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    device_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairTicket
        fields = [
            'id', 'ticket_number', 'client', 'client_id', 'appareil', 'type_appareil',
            'brand', 'model', 'serial_number', 'device_condition',
            'description_panne', 'diagnosis', 'repair_notes', 'internal_notes',
            'technicien', 'technicien_id', 'statut', 'priority',
            'cout_main_oeuvre', 'cout_pieces', 'cout_total', 'discount', 'amount_paid',
            'date_depot', 'date_restitution_prevue', 'date_restitution', 'date_completed',
            'warranty_months', 'warranty_notes', 'accessories', 'password',
            'is_under_warranty', 'is_insured', 'requires_approval',
            'approved_by', 'approved_date', 'date_created', 'date_updated',
            'created_by', 'balance_due', 'is_paid', 'is_overdue', 'device_info'
        ]
        read_only_fields = [
            'id', 'ticket_number', 'date_depot', 'date_created', 'date_updated',
            'created_by', 'cout_total', 'balance_due', 'is_paid', 'is_overdue', 'device_info'
        ]
    
    def get_balance_due(self, obj):
        return float(obj.get_balance_due())
    
    def get_is_paid(self, obj):
        return obj.is_paid()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_device_info(self, obj):
        return obj.get_device_info()


class RepairTicketListSerializer(serializers.ModelSerializer):
    """Simplified repair ticket serializer for lists"""
    
    client = ClientSimpleSerializer(read_only=True)
    technicien = UserSerializer(read_only=True)
    balance_due = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairTicket
        fields = [
            'id', 'ticket_number', 'client', 'appareil', 'type_appareil',
            'technicien', 'statut', 'priority', 'date_depot', 'date_restitution_prevue',
            'cout_total', 'amount_paid', 'balance_due', 'is_paid', 'is_overdue'
        ]
    
    def get_balance_due(self, obj):
        return float(obj.get_balance_due())
    
    def get_is_paid(self, obj):
        return obj.is_paid()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class RepairPartSerializer(serializers.ModelSerializer):
    """Repair part serializer"""
    
    repair_ticket = RepairTicketListSerializer(read_only=True)
    repair_ticket_id = serializers.PrimaryKeyRelatedField(
        queryset=RepairTicket.objects.all(),
        source='repair_ticket',
        write_only=True
    )
    
    inventory_item = InventoryItemSimpleSerializer(read_only=True)
    inventory_item_id = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItem.objects.all(),
        source='inventory_item',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = RepairPart
        fields = [
            'id', 'repair_ticket', 'repair_ticket_id', 'inventory_item', 'inventory_item_id',
            'name', 'description', 'quantity', 'unit_price', 'total_price',
            'serial_number', 'notes', 'date_added'
        ]
        read_only_fields = ['id', 'total_price', 'date_added']


class RepairHistorySerializer(serializers.ModelSerializer):
    """Repair history serializer"""
    
    repair_ticket = RepairTicketListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = RepairHistory
        fields = [
            'id', 'repair_ticket', 'action', 'old_value', 'new_value',
            'notes', 'created_by', 'date_created'
        ]
        read_only_fields = ['id', 'date_created']


class QuickRepairSerializer(serializers.Serializer):
    """Quick repair ticket serializer"""
    
    client_id = serializers.IntegerField()
    appareil = serializers.CharField(max_length=200)
    type_appareil = serializers.ChoiceField(choices=RepairTicket.DeviceType.choices)
    description_panne = serializers.CharField()
    priority = serializers.ChoiceField(choices=RepairTicket.Priority.choices, default=RepairTicket.Priority.NORMAL)
