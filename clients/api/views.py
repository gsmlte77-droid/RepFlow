"""
Clients API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q
from .serializers import (
    ClientSerializer, ClientListSerializer, 
    ClientSimpleSerializer, ClientBalanceSerializer, QuickClientSerializer
)
from ..models import Client


class ClientViewSet(viewsets.ModelViewSet):
    """Client CRUD operations"""
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by client type
        client_type = self.request.query_params.get('client_type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        # Filter by membership status
        membership_status = self.request.query_params.get('membership_status')
        if membership_status:
            queryset = queryset.filter(membership_status=membership_status)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(telephone__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-date_created')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active clients"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search clients"""
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(company_name__icontains=search_term) |
                Q(telephone__icontains=search_term) |
                Q(email__icontains=search_term)
            )
        
        queryset = queryset.order_by('first_name', 'last_name')[:limit]
        serializer = ClientSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get client balance"""
        client = self.get_object()
        serializer = ClientBalanceSerializer(client)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_balance(self, request, pk=None):
        """Update client balance"""
        client = self.get_object()
        amount = request.data.get('amount')
        
        if amount is None:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client.current_balance = float(amount)
            client.save()
            serializer = ClientBalanceSerializer(client)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ClientSearchView(APIView):
    """Client search endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        clients = Client.objects.filter(is_active=True)
        
        if search_term:
            clients = clients.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(company_name__icontains=search_term) |
                Q(telephone__icontains=search_term) |
                Q(email__icontains=search_term)
            )
        
        clients = clients.order_by('first_name', 'last_name')[:limit]
        serializer = ClientSimpleSerializer(clients, many=True)
        return Response(serializer.data)


class ClientBalanceView(APIView):
    """Client balance endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        client = Client.objects.get(pk=pk)
        serializer = ClientBalanceSerializer(client)
        return Response(serializer.data)


class QuickClientView(APIView):
    """Quick client creation endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = QuickClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
