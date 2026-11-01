"""
Billing API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q, Sum
from django.utils import timezone
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer,
    InvoiceItemSerializer, PaymentSerializer, PaymentListSerializer
)
from ..models import Invoice, InvoiceItem, Payment
from clients.models import Client
from accounts.models import User


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice CRUD operations"""
    
    queryset = Invoice.objects.select_related('client', 'repair_ticket', 'created_by').all()
    serializer_class = InvoiceSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
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
        
        # Filter by repair ticket
        repair_ticket_id = self.request.query_params.get('repair_ticket_id')
        if repair_ticket_id:
            queryset = queryset.filter(repair_ticket_id=repair_ticket_id)
        
        # Filter by status
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filter by credit status
        statut_credit = self.request.query_params.get('statut_credit')
        if statut_credit:
            queryset = queryset.filter(statut_credit=statut_credit)
        
        # Filter by invoice type
        invoice_type = self.request.query_params.get('invoice_type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(invoice_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(invoice_date__lte=date_to)
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue is not None:
            if is_overdue.lower() == 'true':
                queryset = queryset.filter(
                    due_date__lt=timezone.now().date(),
                    balance_due__gt=0
                )
            else:
                queryset = queryset.exclude(
                    due_date__lt=timezone.now().date(),
                    balance_due__gt=0
                )
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(
                    Q(balance_due__gt=0) |
                    Q(statut__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID, Invoice.Status.SENT])
                )
        
        return queryset.order_by('-invoice_date', '-date_created')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active invoices"""
        queryset = self.get_queryset().exclude(
            statut__in=[Invoice.Status.CANCELLED, Invoice.Status.REFUNDED]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices"""
        queryset = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            balance_due__gt=0
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unpaid(self, request):
        """Get unpaid invoices"""
        queryset = self.get_queryset().filter(balance_due__gt=0)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update invoice status"""
        invoice = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        invoice.statut = new_status
        if new_status == Invoice.Status.SENT:
            invoice.sent_date = timezone.now()
        elif new_status == Invoice.Status.PAID:
            invoice.paid_date = timezone.now()
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send invoice"""
        invoice = self.get_object()
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        invoice.statut = Invoice.Status.SENT
        invoice.sent_date = timezone.now()
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """Invoice item CRUD operations"""
    
    queryset = InvoiceItem.objects.select_related('invoice').all()
    serializer_class = InvoiceItemSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by invoice
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(
                    invoice__balance_due__gt=0
                )
        
        return queryset.order_by('order')
    
    def perform_create(self, serializer):
        serializer.save()


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment CRUD operations"""
    
    queryset = Payment.objects.select_related('invoice', 'invoice__client', 'created_by').all()
    serializer_class = PaymentSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by invoice
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(transaction_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__date__lte=date_to)
        
        # Apply user permissions
        if not self.request.user.is_admin():
            if self.request.user.role == User.Role.CASHIER:
                queryset = queryset.filter(created_by=self.request.user)
        
        return queryset.order_by('-transaction_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InvoiceSearchView(APIView):
    """Invoice search endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        search_term = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 10))
        
        invoices = Invoice.objects.select_related('client').filter(
            statut__in=[Invoice.Status.PENDING, Invoice.Status.SENT, Invoice.Status.PARTIALLY_PAID]
        )
        
        # Apply user permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                invoices = invoices.filter(
                    Q(balance_due__gt=0) |
                    Q(statut__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID, Invoice.Status.SENT])
                )
        
        if search_term:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search_term) |
                Q(reference__icontains=search_term) |
                Q(client__first_name__icontains=search_term) |
                Q(client__last_name__icontains=search_term) |
                Q(client__telephone__icontains=search_term)
            )
        
        invoices = invoices.order_by('-invoice_date')[:limit]
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


class InvoiceStatsView(APIView):
    """Invoice statistics endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        invoices = Invoice.objects.all()
        
        # Apply user permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                invoices = invoices.filter(
                    Q(balance_due__gt=0) |
                    Q(statut__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID, Invoice.Status.SENT])
                )
        
        stats = {
            'total': invoices.count(),
            'draft': invoices.filter(statut=Invoice.Status.DRAFT).count(),
            'pending': invoices.filter(statut=Invoice.Status.PENDING).count(),
            'sent': invoices.filter(statut=Invoice.Status.SENT).count(),
            'paid': invoices.filter(statut=Invoice.Status.PAID).count(),
            'partially_paid': invoices.filter(statut=Invoice.Status.PARTIALLY_PAID).count(),
            'cancelled': invoices.filter(statut=Invoice.Status.CANCELLED).count(),
            'refunded': invoices.filter(statut=Invoice.Status.REFUNDED).count(),
            'overdue': invoices.filter(
                due_date__lt=timezone.now().date(),
                balance_due__gt=0
            ).count(),
            'total_amount': float(invoices.aggregate(total=Sum('total'))['total'] or 0),
            'total_paid': float(invoices.aggregate(total=Sum('amount_paid'))['total'] or 0),
            'total_outstanding': float(invoices.aggregate(total=Sum('balance_due'))['total'] or 0),
            'credit_in_progress': invoices.filter(statut_credit='EN_COURS').count(),
            'credit_settled': invoices.filter(statut_credit='SOLDE').count(),
            'today': invoices.filter(invoice_date=timezone.now().date()).count(),
            'this_week': invoices.filter(invoice_date__gte=timezone.now().date() - timezone.timedelta(days=7)).count(),
            'this_month': invoices.filter(invoice_date__month=timezone.now().month).count()
        }
        
        return Response(stats)


class InvoiceStatusView(APIView):
    """Invoice status update endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        invoice = Invoice.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.statut = new_status
        if new_status == Invoice.Status.SENT:
            invoice.sent_date = timezone.now()
        elif new_status == Invoice.Status.PAID:
            invoice.paid_date = timezone.now()
        invoice.save()
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class InvoiceSendView(APIView):
    """Invoice send endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        invoice = Invoice.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        invoice.statut = Invoice.Status.SENT
        invoice.sent_date = timezone.now()
        invoice.save()
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class InvoiceItemsView(APIView):
    """Invoice items endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        invoice = Invoice.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER and invoice.client != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        items = InvoiceItem.objects.filter(invoice=invoice).order_by('order')
        serializer = InvoiceItemSerializer(items, many=True)
        return Response(serializer.data)


class InvoicePaymentsView(APIView):
    """Invoice payments endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        invoice = Invoice.objects.get(pk=pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER and invoice.client != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        payments = Payment.objects.filter(invoice=invoice).order_by('-transaction_date')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class ClientInvoicesView(APIView):
    """Client invoices endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, client_pk):
        client = Client.objects.get(pk=client_pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER and client != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        invoices = Invoice.objects.filter(client=client).select_related('repair_ticket').order_by('-invoice_date')
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


class ClientBalanceView(APIView):
    """Client balance endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, client_pk):
        client = Client.objects.get(pk=client_pk)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER and client != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Calculate total outstanding balance
        invoices = Invoice.objects.filter(client=client, balance_due__gt=0)
        total_outstanding = sum(float(invoice.balance_due) for invoice in invoices)
        
        # Calculate total paid
        total_paid = sum(float(invoice.amount_paid) for invoice in Invoice.objects.filter(client=client))
        
        data = {
            'total_outstanding': total_outstanding,
            'total_paid': total_paid,
            'total_invoices': Invoice.objects.filter(client=client).count(),
            'overdue_invoices': Invoice.objects.filter(
                client=client,
                due_date__lt=timezone.now().date(),
                balance_due__gt=0
            ).count()
        }
        
        return Response(data)
