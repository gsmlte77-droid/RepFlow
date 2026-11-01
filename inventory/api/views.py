"""
Inventory API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q, Sum, Count
from .serializers import (
    InventoryItemSerializer, InventoryItemListSerializer,
    InventoryItemSimpleSerializer, CategorySerializer,
    SupplierSerializer, StockMovementSerializer
)
from ..models import InventoryItem, Category, Supplier, StockMovement
from config.models import AppConfig


class InventoryItemViewSet(viewsets.ModelViewSet):
    """Inventory item CRUD operations"""
    
    queryset = InventoryItem.objects.select_related('category', 'supplier').all()
    serializer_class = InventoryItemSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryItemListSerializer
        return InventoryItemSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Filter by item type
        item_type = self.request.query_params.get('item_type')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status')
        if stock_status:
            config = AppConfig.get_instance()
            threshold = config.low_stock_threshold
            
            if stock_status == 'IN_STOCK':
                queryset = queryset.filter(quantite_stock__gt=threshold)
            elif stock_status == 'LOW_STOCK':
                queryset = queryset.filter(
                    quantite_stock__gt=0,
                    quantite_stock__lte=threshold
                )
            elif stock_status == 'OUT_OF_STOCK':
                queryset = queryset.filter(quantite_stock=0)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(reference_sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active items"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search items"""
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(reference_sku__icontains=search_term) |
                Q(barcode__icontains=search_term)
            )
        
        queryset = queryset.order_by('name')[:limit]
        serializer = InventoryItemSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        """Update item stock"""
        item = self.get_object()
        quantity = request.data.get('quantity')
        operation = request.data.get('operation', 'add')
        notes = request.data.get('notes', '')
        
        if quantity is None:
            return Response(
                {'error': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            
            if operation == 'add':
                new_stock = item.update_stock(quantity, 'add')
            elif operation == 'subtract':
                if item.quantite_stock < quantity:
                    return Response(
                        {'error': 'Insufficient stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_stock = item.update_stock(quantity, 'subtract')
                
                # Create stock movement
                StockMovement.objects.create(
                    item=item,
                    movement_type=StockMovement.MovementType.SALE,
                    quantity=quantity,
                    quantity_before=item.quantite_stock + quantity,
                    quantity_after=new_stock,
                    reference=f"API-{request.user.username}" if request.user.is_authenticated else "API",
                    notes=notes,
                    created_by=request.user if request.user.is_authenticated else None
                )
            else:
                return Response(
                    {'error': 'Invalid operation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """Category CRUD operations"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return super().get_queryset().order_by('name')


class SupplierViewSet(viewsets.ModelViewSet):
    """Supplier CRUD operations"""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return super().get_queryset().order_by('name')


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Stock movement read-only operations"""
    
    serializer_class = StockMovementSerializer
    
    def get_queryset(self):
        return StockMovement.objects.select_related('item', 'created_by').all().order_by('-date_created')


class InventorySearchView(APIView):
    """Inventory search endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        items = InventoryItem.objects.filter(is_active=True)
        
        if search_term:
            items = items.filter(
                Q(name__icontains=search_term) |
                Q(reference_sku__icontains=search_term) |
                Q(barcode__icontains=search_term)
            )
        
        items = items.order_by('name')[:limit]
        serializer = InventoryItemSimpleSerializer(items, many=True)
        return Response(serializer.data)


class LowStockView(APIView):
    """Low stock items endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config = AppConfig.get_instance()
        threshold = config.low_stock_threshold
        
        items = InventoryItem.objects.filter(
            is_active=True,
            quantite_stock__gt=0,
            quantite_stock__lte=threshold
        ).select_related('category')
        
        serializer = InventoryItemListSerializer(items, many=True)
        return Response(serializer.data)


class InventoryStatsView(APIView):
    """Inventory statistics endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config = AppConfig.get_instance()
        
        stats = {
            'total_items': InventoryItem.objects.filter(is_active=True).count(),
            'total_value': float(InventoryItem.objects.filter(is_active=True).aggregate(
                total=Sum('quantite_stock') * Sum('prix_achat')
            )['total'] or 0),
            'low_stock': InventoryItem.objects.filter(
                is_active=True,
                quantite_stock__gt=0,
                quantite_stock__lte=config.low_stock_threshold
            ).count(),
            'out_of_stock': InventoryItem.objects.filter(
                is_active=True,
                quantite_stock=0
            ).count(),
            'by_category': list(InventoryItem.objects.filter(is_active=True).values('category__name').annotate(
                count=Count('id')
            ).order_by('category__name')),
            'by_type': list(InventoryItem.objects.filter(is_active=True).values('item_type').annotate(
                count=Count('id')
            ).order_by('item_type')),
        }
        
        return Response(stats)


class ItemStockView(APIView):
    """Item stock endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        item = InventoryItem.objects.get(pk=pk)
        serializer = InventoryItemSerializer(item)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        item = InventoryItem.objects.get(pk=pk)
        quantity = request.data.get('quantity')
        operation = request.data.get('operation', 'add')
        notes = request.data.get('notes', '')
        
        if quantity is None:
            return Response(
                {'error': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            
            if operation == 'add':
                new_stock = item.update_stock(quantity, 'add')
            elif operation == 'subtract':
                if item.quantite_stock < quantity:
                    return Response(
                        {'error': 'Insufficient stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_stock = item.update_stock(quantity, 'subtract')
                
                # Create stock movement
                StockMovement.objects.create(
                    item=item,
                    movement_type=StockMovement.MovementType.SALE,
                    quantity=quantity,
                    quantity_before=item.quantite_stock + quantity,
                    quantity_after=new_stock,
                    reference=f"API-{request.user.username}" if request.user.is_authenticated else "API",
                    notes=notes,
                    created_by=request.user if request.user.is_authenticated else None
                )
            else:
                return Response(
                    {'error': 'Invalid operation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = InventoryItemSerializer(item)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
