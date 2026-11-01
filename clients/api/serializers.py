"""
Clients API serializers
"""
from rest_framework import serializers
from ..models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Client serializer"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'company_name', 'client_type',
            'telephone', 'secondary_telephone', 'email', 'secondary_email',
            'address', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'registration_number', 'credit_limit', 'current_balance',
            'membership_status', 'discount_rate', 'referral_source', 'notes',
            'is_active', 'is_blacklisted', 'date_created', 'date_updated',
            'last_contact_date'
        ]
        read_only_fields = ['date_created', 'date_updated']


class ClientListSerializer(serializers.ModelSerializer):
    """Simplified client serializer for lists"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'company_name', 'client_type',
            'telephone', 'email', 'current_balance', 'membership_status',
            'is_active', 'is_blacklisted', 'date_created'
        ]


class ClientSimpleSerializer(serializers.ModelSerializer):
    """Minimal client serializer for dropdowns"""
    
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'telephone']
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.get_display_name(),
            'telephone': instance.telephone,
            'email': instance.email,
            'balance': float(instance.current_balance)
        }


class ClientBalanceSerializer(serializers.ModelSerializer):
    """Client balance serializer"""
    
    class Meta:
        model = Client
        fields = ['id', 'current_balance', 'credit_limit', 'discount_rate']


class QuickClientSerializer(serializers.ModelSerializer):
    """Quick client serializer for fast entry"""
    
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'telephone', 'email', 'address']
