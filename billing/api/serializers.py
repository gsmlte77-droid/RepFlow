"""
Billing API serializers
"""
from rest_framework import serializers
from ..models import Invoice, InvoiceItem, Payment
from clients.api.serializers import ClientSimpleSerializer
from repairs.api.serializers import RepairTicketListSerializer
from accounts.api.serializers import UserSerializer


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer"""
    
    client = ClientSimpleSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    
    repair_ticket = RepairTicketListSerializer(read_only=True)
    repair_ticket_id = serializers.PrimaryKeyRelatedField(
        queryset=RepairTicket.objects.all(),
        source='repair_ticket',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    created_by = UserSerializer(read_only=True)
    
    balance_due = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_id', 'repair_ticket', 'repair_ticket_id',
            'invoice_type', 'invoice_date', 'due_date', 'reference',
            'subtotal', 'tax_rate', 'tax_amount', 'discount', 'total',
            'amount_paid', 'balance_due', 'statut', 'statut_credit', 'reste_a_payer',
            'payment_terms', 'notes', 'internal_notes',
            'date_created', 'date_updated', 'created_by', 'sent_date', 'paid_date',
            'is_paid', 'is_overdue', 'days_overdue'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'date_created', 'date_updated',
            'created_by', 'tax_amount', 'total', 'balance_due',
            'reste_a_payer', 'is_paid', 'is_overdue', 'days_overdue',
            'sent_date', 'paid_date'
        ]
    
    def get_balance_due(self, obj):
        return float(obj.balance_due)
    
    def get_is_paid(self, obj):
        return obj.is_paid()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_days_overdue(self, obj):
        return obj.get_days_overdue()


class InvoiceListSerializer(serializers.ModelSerializer):
    """Simplified invoice serializer for lists"""
    
    client = ClientSimpleSerializer(read_only=True)
    repair_ticket = RepairTicketListSerializer(read_only=True)
    balance_due = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'repair_ticket',
            'invoice_type', 'invoice_date', 'due_date', 'total',
            'amount_paid', 'balance_due', 'statut', 'statut_credit',
            'is_paid', 'is_overdue'
        ]
    
    def get_balance_due(self, obj):
        return float(obj.balance_due)
    
    def get_is_paid(self, obj):
        return obj.is_paid()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Invoice item serializer"""
    
    invoice = InvoiceListSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(),
        source='invoice',
        write_only=True
    )
    
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'invoice_id', 'description', 'quantity',
            'unit_price', 'tax_rate', 'total', 'order'
        ]
        read_only_fields = ['id', 'total']
    
    def get_total(self, obj):
        return float(obj.total)


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    
    invoice = InvoiceListSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(),
        source='invoice',
        write_only=True
    )
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_id', 'amount', 'payment_method',
            'reference', 'notes', 'transaction_date', 'created_by',
            'date_created', 'date_updated'
        ]
        read_only_fields = ['id', 'transaction_date', 'created_by', 'date_created', 'date_updated']


class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified payment serializer for lists"""
    
    invoice = InvoiceListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'amount', 'payment_method', 'reference',
            'transaction_date', 'created_by', 'date_created'
        ]
