"""
Config API serializers
"""
from rest_framework import serializers
from ..models import AppConfig


class AppConfigSerializer(serializers.ModelSerializer):
    """AppConfig serializer"""
    
    class Meta:
        model = AppConfig
        fields = [
            'id', 'company_name', 'company_slogan', 'phone', 'email', 'website',
            'address', 'city', 'postal_code', 'country', 'currency',
            'tax_rate', 'discount_rate', 'invoice_prefix', 'invoice_start_number',
            'invoice_footer_text', 'invoice_terms', 'default_language',
            'timezone', 'date_format', 'business_hours', 'max_credit_days',
            'credit_enabled', 'low_stock_threshold', 'email_notifications',
            'sms_notifications', 'system_name', 'version', 'maintenance_mode',
            'date_created', 'date_updated'
        ]
        read_only_fields = ['id', 'date_created', 'date_updated']


class AppConfigSimpleSerializer(serializers.ModelSerializer):
    """Simplified AppConfig serializer for public endpoints"""
    
    class Meta:
        model = AppConfig
        fields = [
            'company_name', 'company_slogan', 'phone', 'email',
            'address', 'currency', 'tax_rate', 'invoice_prefix',
            'invoice_footer_text', 'logo', 'favicon'
        ]
