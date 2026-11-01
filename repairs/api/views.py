"""
Repairs API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .serializers import (
    RepairTicketSerializer, RepairTicketListSerializer,
    RepairPartSerializer, RepairHistorySerializer, QuickRepairSerializer
)
from ..models import RepairTicket, RepairPart, RepairHistory
from clients.models import Client
from accounts.models import User


class RepairTicketViewSet(viewsets.ModelViewSet):
    """Repair ticket CRUD operations"""
    
    queryset = RepairTicket.objects.select_related('client', 'technicien', 'created_by').all()
    serializer_class = RepairTicketSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RepairTicketListSerializer
        return RepairTicketSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by client
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by technician
        technicien_id = self.request.query_params.get('technicien_id')
        if technicien_id:
            queryset = queryset.filter(technicien_id=technicien_id)
        
        # Filter by status
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by device type
        type_appareil = self.request.query_params.get('type_appareil')
        if type_appareil:
            queryset = queryset.filter(type_appareil=type_appareil)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date_depot__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_depot__date__lte=date_to)
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue is not None:
            if is_overdue.lower() == 'true':
                queryset = queryset.filter(
                    date_restitution_prevue__lt=timezone.now().date(),
                    statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
                )
            else:
                queryset = queryset.exclude(
                    date_restitution_prevue__lt=timezone.now().date(),
                    statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
                )
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.TECHNICIAN:
                queryset = queryset.filter(technicien=self.request.user)
            elif self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(
                    Q(statut=RepairTicket.Status.READY) |
                    Q(statut=RepairTicket.Status.DELIVERED) |
                    Q(statut=RepairTicket.Status.QUOTATION)
                )
        
        return queryset.order_by('-date_depot')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active tickets"""
        queryset = self.get_queryset().exclude(
            statut__in=[RepairTicket.Status.CANCELLED, RepairTicket.Status.REJECTED]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending tickets"""
        queryset = self.get_queryset().filter(statut=RepairTicket.Status.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tickets"""
        queryset = self.get_queryset().filter(
            date_restitution_prevue__lt=timezone.now().date(),
            statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update ticket status"""
        ticket = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = ticket.statut
        ticket.statut = new_status
        ticket.save()
        
        # Add to history
        RepairHistory.objects.create(
            repair_ticket=ticket,
            action=RepairHistory.Action.STATUS_CHANGED,
            old_value=old_status,
            new_value=new_status,
            notes=notes,
            created_by=request.user
        )
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)


class RepairPartViewSet(viewsets.ModelViewSet):
    """Repair part CRUD operations"""
    
    queryset = RepairPart.objects.select_related('repair_ticket', 'inventory_item').all()
    serializer_class = RepairPartSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by repair ticket
        repair_ticket_id = self.request.query_params.get('repair_ticket_id')
        if repair_ticket_id:
            queryset = queryset.filter(repair_ticket_id=repair_ticket_id)
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.TECHNICIAN:
                queryset = queryset.filter(repair_ticket__technicien=self.request.user)
            elif self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(
                    repair_ticket__statut__in=[
                        RepairTicket.Status.READY,
                        RepairTicket.Status.DELIVERED,
                        RepairTicket.Status.QUOTATION
                    ]
                )
        
        return queryset.order_by('-date_added')
    
    def perform_create(self, serializer):
        part = serializer.save()
        
        # Update repair ticket costs
        part.repair_ticket.cout_pieces = sum(
            p.total_price for p in part.repair_ticket.repair_parts.all()
        )
        part.repair_ticket.cout_total = (
            part.repair_ticket.cout_main_oeuvre + 
            part.repair_ticket.cout_pieces - 
            part.repair_ticket.discount
        )
        part.repair_ticket.save()
        
        # Update inventory stock
        if part.inventory_item:
            try:
                part.inventory_item.update_stock(part.quantity, 'subtract')
            except ValueError:
                pass  # Handle in serializer validation
    
    def perform_destroy(self, instance):
        # Return inventory to stock
        if instance.inventory_item:
            instance.inventory_item.update_stock(instance.quantity, 'add')
        
        # Update repair ticket costs
        instance.repair_ticket.cout_pieces = sum(
            p.total_price for p in instance.repair_ticket.repair_parts.all() 
            if p.pk != instance.pk
        )
        instance.repair_ticket.cout_total = (
            instance.repair_ticket.cout_main_oeuvre + 
            instance.repair_ticket.cout_pieces - 
            instance.repair_ticket.discount
        )
        instance.repair_ticket.save()
        
        super().perform_destroy(instance)


class RepairHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Repair history read-only operations"""
    
    serializer_class = RepairHistorySerializer
    
    def get_queryset(self):
        queryset = RepairHistory.objects.select_related('repair_ticket', 'created_by').all()
        
        # Filter by repair ticket
        repair_ticket_id = self.request.query_params.get('repair_ticket_id')
        if repair_ticket_id:
            queryset = queryset.filter(repair_ticket_id=repair_ticket_id)
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.TECHNICIAN:
                queryset = queryset.filter(repair_ticket__technicien=self.request.user)
            elif self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(
                    repair_ticket__statut__in=[
                        RepairTicket.Status.READY,
                        RepairTicket.Status.DELIVERED,
                        RepairTicket.Status.QUOTATION
                    ]
                )
        
        return queryset.order_by('-date_created')


class RepairSearchView(APIView):
    """Repair ticket search endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        tickets = RepairTicket.objects.select_related('client', 'technicien').filter(
            statut__in=[
                RepairTicket.Status.PENDING,
                RepairTicket.Status.DIAGNOSIS,
                RepairTicket.Status.IN_PROGRESS,
                RepairTicket.Status.WAITING_PARTS,
                RepairTicket.Status.QUOTATION,
                RepairTicket.Status.READY
            ]
        )
        
        # Apply user permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.TECHNICIAN:
                tickets = tickets.filter(technicien=request.user)
            elif request.user.role == User.Role.CASHIER:
                tickets = tickets.filter(
                    Q(statut=RepairTicket.Status.READY) |
                    Q(statut=RepairTicket.Status.DELIVERED) |
                    Q(statut=RepairTicket.Status.QUOTATION)
                )
        
        if search_term:
            tickets = tickets.filter(
                Q(ticket_number__icontains=search_term) |
                Q(appareil__icontains=search_term) |
                Q(client__first_name__icontains=search_term) |
                Q(client__last_name__icontains=search_term) |
                Q(client__telephone__icontains=search_term)
            )
        
        tickets = tickets.order_by('-date_depot')[:limit]
        serializer = RepairTicketListSerializer(tickets, many=True)
        return Response(serializer.data)


class RepairStatsView(APIView):
    """Repair statistics endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Apply user permissions
        tickets = RepairTicket.objects.all()
        
        if not request.user.is_admin():
            if request.user.role == User.Role.TECHNICIAN:
                tickets = tickets.filter(technicien=request.user)
            elif request.user.role == User.Role.CASHIER:
                tickets = tickets.filter(
                    Q(statut=RepairTicket.Status.READY) |
                    Q(statut=RepairTicket.Status.DELIVERED) |
                    Q(statut=RepairTicket.Status.QUOTATION)
                )
        
        stats = {
            'total': tickets.count(),
            'pending': tickets.filter(statut=RepairTicket.Status.PENDING).count(),
            'diagnosis': tickets.filter(statut=RepairTicket.Status.DIAGNOSIS).count(),
            'in_progress': tickets.filter(statut=RepairTicket.Status.IN_PROGRESS).count(),
            'waiting_parts': tickets.filter(statut=RepairTicket.Status.WAITING_PARTS).count(),
            'quotation': tickets.filter(statut=RepairTicket.Status.QUOTATION).count(),
            'ready': tickets.filter(statut=RepairTicket.Status.READY).count(),
            'delivered': tickets.filter(statut=RepairTicket.Status.DELIVERED).count(),
            'cancelled': tickets.filter(statut=RepairTicket.Status.CANCELLED).count(),
            'rejected': tickets.filter(statut=RepairTicket.Status.REJECTED).count(),
            'overdue': tickets.filter(
                date_restitution_prevue__lt=timezone.now().date(),
                statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
            ).count(),
            'by_priority': list(tickets.values('priority').annotate(count=Count('id')).order_by('priority')),
            'by_device_type': list(tickets.values('type_appareil').annotate(count=Count('id')).order_by('type_appareil')),
            'total_revenue': float(tickets.aggregate(total=Sum('cout_total'))['total'] or 0),
            'total_outstanding': float(tickets.aggregate(total=Sum('cout_total') - Sum('amount_paid'))['total'] or 0),
            'today': tickets.filter(date_depot__date=timezone.now().date()).count(),
            'this_week': tickets.filter(date_depot__date__gte=timezone.now().date() - timezone.timedelta(days=7)).count(),
            'this_month': tickets.filter(date_depot__date__month=timezone.now().month).count()
        }
        
        return Response(stats)


class TicketStatusView(APIView):
    """Ticket status update endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        ticket = RepairTicket.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = ticket.statut
        ticket.statut = new_status
        ticket.save()
        
        # Add to history
        RepairHistory.objects.create(
            repair_ticket=ticket,
            action=RepairHistory.Action.STATUS_CHANGED,
            old_value=old_status,
            new_value=new_status,
            notes=notes,
            created_by=request.user
        )
        
        serializer = RepairTicketSerializer(ticket)
        return Response(serializer.data)


class TicketPartsView(APIView):
    """Ticket parts endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        ticket = RepairTicket.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        parts = RepairPart.objects.filter(repair_ticket=ticket).select_related('inventory_item')
        serializer = RepairPartSerializer(parts, many=True)
        return Response(serializer.data)


class TicketHistoryView(APIView):
    """Ticket history endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        ticket = RepairTicket.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        history = RepairHistory.objects.filter(repair_ticket=ticket).select_related('created_by').order_by('-date_created')
        serializer = RepairHistorySerializer(history, many=True)
        return Response(serializer.data)


class QuickRepairView(APIView):
    """Quick repair ticket creation endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = QuickRepairSerializer(data=request.data)
        if serializer.is_valid():
            client = Client.objects.get(pk=serializer.validated_data['client_id'])
            
            ticket = RepairTicket.objects.create(
                client=client,
                appareil=serializer.validated_data['appareil'],
                type_appareil=serializer.validated_data['type_appareil'],
                description_panne=serializer.validated_data['description_panne'],
                priority=serializer.validated_data['priority'],
                created_by=request.user
            )
            
            return Response(RepairTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
