"""
Config API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import AppConfigSerializer, AppConfigSimpleSerializer
from ..models import AppConfig


class AppConfigViewSet(viewsets.ModelViewSet):
    """AppConfig CRUD operations"""
    
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_object(self):
        """Override to always return the singleton instance"""
        return AppConfig.get_instance()
    
    def list(self, request, *args, **kwargs):
        """Override list to return only the singleton instance"""
        config = self.get_object()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Prevent creating multiple instances"""
        return Response(
            {'error': 'Only one configuration instance is allowed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of the singleton instance"""
        return Response(
            {'error': 'Cannot delete the configuration instance.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """Get public configuration (read-only)"""
        config = self.get_object()
        serializer = AppConfigSimpleSerializer(config)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def currency(self, request):
        """Get currency settings"""
        config = self.get_object()
        return Response({
            'currency': config.currency,
            'symbol': self.get_currency_symbol(config.currency)
        })
    
    @action(detail=False, methods=['get'])
    def tax(self, request):
        """Get tax settings"""
        config = self.get_object()
        return Response({
            'tax_rate': float(config.tax_rate),
            'discount_rate': float(config.discount_rate)
        })
    
    def get_currency_symbol(self, currency_code):
        """Get currency symbol from code"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'DZD': 'د.ج',
            'MAD': 'د.م.',
            'TND': 'د.ت',
            'SAR': 'ر.س',
            'AED': 'د.إ',
            'QAR': 'ر.ق',
        }
        return symbols.get(currency_code, currency_code)
