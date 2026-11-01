"""
Dashboard API views
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum
from django.utils import timezone
from repairs.models import RepairTicket
from clients.models import Client
from inventory.models import InventoryItem
from billing.models import Invoice, Payment
from config.models import AppConfig
from accounts.models import User


class DashboardStatsView(APIView):
    """Dashboard statistics endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config = AppConfig.get_instance()
        
        # Get statistics based on user role
        if request.user.is_admin():
            total_repairs = RepairTicket.objects.count()
            pending_repairs = RepairTicket.objects.filter(
                statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.DIAGNOSIS]
            ).count()
            in_progress_repairs = RepairTicket.objects.filter(
                statut=RepairTicket.Status.IN_PROGRESS
            ).count()
            ready_repairs = RepairTicket.objects.filter(
                statut=RepairTicket.Status.READY
            ).count()
            delivered_repairs = RepairTicket.objects.filter(
                statut=RepairTicket.Status.DELIVERED
            ).count()
            
            total_clients = Client.objects.filter(is_active=True).count()
            new_clients_this_month = Client.objects.filter(
                is_active=True,
                date_created__month=timezone.now().month
            ).count()
            
            total_inventory = InventoryItem.objects.filter(is_active=True).count()
            low_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock__lte=config.low_stock_threshold
            ).count()
            out_of_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock=0
            ).count()
            
            total_revenue = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
            total_outstanding = Invoice.objects.aggregate(total=Sum('balance_due'))['total'] or 0
            total_paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
            
            overdue_invoices = Invoice.objects.filter(
                due_date__lt=timezone.now().date(),
                balance_due__gt=0
            ).count()
            
            credit_in_progress = Invoice.objects.filter(statut_credit='EN_COURS').count()
            credit_settled = Invoice.objects.filter(statut_credit='SOLDE').count()
            
        elif request.user.role == User.Role.TECHNICIAN:
            total_repairs = RepairTicket.objects.filter(technicien=request.user).count()
            pending_repairs = RepairTicket.objects.filter(
                technicien=request.user,
                statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.DIAGNOSIS]
            ).count()
            in_progress_repairs = RepairTicket.objects.filter(
                technicien=request.user,
                statut=RepairTicket.Status.IN_PROGRESS
            ).count()
            ready_repairs = RepairTicket.objects.filter(
                technicien=request.user,
                statut=RepairTicket.Status.READY
            ).count()
            delivered_repairs = RepairTicket.objects.filter(
                technicien=request.user,
                statut=RepairTicket.Status.DELIVERED
            ).count()
            
            total_clients = 0
            new_clients_this_month = 0
            
            total_inventory = InventoryItem.objects.filter(is_active=True).count()
            low_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock__lte=config.low_stock_threshold
            ).count()
            out_of_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock=0
            ).count()
            
            total_revenue = 0
            total_outstanding = 0
            total_paid = 0
            overdue_invoices = 0
            credit_in_progress = 0
            credit_settled = 0
            
        elif request.user.role == User.Role.CASHIER:
            total_repairs = RepairTicket.objects.count()
            pending_repairs = 0
            in_progress_repairs = 0
            ready_repairs = RepairTicket.objects.filter(
                statut=RepairTicket.Status.READY
            ).count()
            delivered_repairs = RepairTicket.objects.filter(
                statut=RepairTicket.Status.DELIVERED
            ).count()
            
            total_clients = Client.objects.filter(is_active=True).count()
            new_clients_this_month = Client.objects.filter(
                is_active=True,
                date_created__month=timezone.now().month
            ).count()
            
            total_inventory = InventoryItem.objects.filter(is_active=True).count()
            low_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock__lte=config.low_stock_threshold
            ).count()
            out_of_stock_items = InventoryItem.objects.filter(
                is_active=True,
                quantite_stock=0
            ).count()
            
            total_revenue = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
            total_outstanding = Invoice.objects.aggregate(total=Sum('balance_due'))['total'] or 0
            total_paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
            
            overdue_invoices = Invoice.objects.filter(
                due_date__lt=timezone.now().date(),
                balance_due__gt=0
            ).count()
            
            credit_in_progress = Invoice.objects.filter(statut_credit='EN_COURS').count()
            credit_settled = Invoice.objects.filter(statut_credit='SOLDE').count()
        else:
            total_repairs = 0
            pending_repairs = 0
            in_progress_repairs = 0
            ready_repairs = 0
            delivered_repairs = 0
            
            total_clients = 0
            new_clients_this_month = 0
            
            total_inventory = 0
            low_stock_items = 0
            out_of_stock_items = 0
            
            total_revenue = 0
            total_outstanding = 0
            total_paid = 0
            overdue_invoices = 0
            credit_in_progress = 0
            credit_settled = 0
        
        stats = {
            'total_repairs': total_repairs,
            'pending_repairs': pending_repairs,
            'in_progress_repairs': in_progress_repairs,
            'ready_repairs': ready_repairs,
            'delivered_repairs': delivered_repairs,
            'total_clients': total_clients,
            'new_clients_this_month': new_clients_this_month,
            'total_inventory': total_inventory,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_revenue': float(total_revenue),
            'total_outstanding': float(total_outstanding),
            'total_paid': float(total_paid),
            'overdue_invoices': overdue_invoices,
            'credit_in_progress': credit_in_progress,
            'credit_settled': credit_settled,
        }
        
        return Response(stats)


class DashboardRepairsView(APIView):
    """Dashboard repairs endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get repairs based on user role
        if request.user.is_admin():
            repairs = RepairTicket.objects.select_related('client', 'technicien').order_by('-date_depot')[:10]
        elif request.user.role == User.Role.TECHNICIAN:
            repairs = RepairTicket.objects.filter(
                technicien=request.user
            ).select_related('client').order_by('-date_depot')[:10]
        elif request.user.role == User.Role.CASHIER:
            repairs = RepairTicket.objects.filter(
                statut__in=[RepairTicket.Status.READY, RepairTicket.Status.DELIVERED]
            ).select_related('client', 'technicien').order_by('-date_depot')[:10]
        else:
            repairs = []
        
        data = [{
            'id': repair.id,
            'ticket_number': repair.ticket_number,
            'client_name': repair.client.get_display_name(),
            'device': repair.get_device_info(),
            'statut': repair.statut,
            'statut_display': repair.get_statut_display(),
            'priority': repair.priority,
            'priority_display': repair.get_priority_display(),
            'date_depot': repair.date_depot.strftime('%Y-%m-%d %H:%M') if repair.date_depot else None,
            'date_restitution_prevue': repair.date_restitution_prevue.strftime('%Y-%m-%d') if repair.date_restitution_prevue else None,
            'cout_total': float(repair.cout_total),
            'is_overdue': repair.is_overdue()
        } for repair in repairs]
        
        return Response(data)


class DashboardFinancialView(APIView):
    """Dashboard financial endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get financial data based on user role
        if request.user.is_admin() or request.user.role == User.Role.CASHIER:
            invoices = Invoice.objects.select_related('client').order_by('-invoice_date')[:10]
            
            # Charts data
            revenue_by_month = list(Invoice.objects.extra(
                {'month': "strftime('%Y-%m', invoice_date)"}
            ).values('month').annotate(total=Sum('total')).order_by('month'))
            
            payments_by_method = list(Payment.objects.values('payment_method').annotate(
                total=Sum('amount')
            ).order_by('payment_method'))
        else:
            invoices = []
            revenue_by_month = []
            payments_by_method = []
        
        data = {
            'recent_invoices': [{
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client.get_display_name(),
                'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
                'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
                'total': float(invoice.total),
                'amount_paid': float(invoice.amount_paid),
                'balance_due': float(invoice.balance_due),
                'statut': invoice.statut,
                'statut_display': invoice.get_statut_display(),
                'is_overdue': invoice.is_overdue()
            } for invoice in invoices],
            'charts': {
                'revenue_by_month': revenue_by_month,
                'payments_by_method': payments_by_method,
            }
        }
        
        return Response(data)


class DashboardInventoryView(APIView):
    """Dashboard inventory endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        config = AppConfig.get_instance()
        
        # Get inventory data
        low_stock_items = InventoryItem.objects.filter(
            is_active=True,
            quantite_stock__lte=config.low_stock_threshold,
            quantite_stock__gt=0
        ).select_related('category').order_by('name')[:10]
        
        out_of_stock_items = InventoryItem.objects.filter(
            is_active=True,
            quantite_stock=0
        ).select_related('category').order_by('name')[:10]
        
        data = {
            'low_stock_items': [{
                'id': item.id,
                'name': item.name,
                'reference_sku': item.reference_sku,
                'stock': item.quantite_stock,
                'alert_threshold': item.seuil_alerte,
                'category': item.category.name if item.category else None,
                'purchase_price': float(item.prix_achat),
                'selling_price': float(item.prix_vente)
            } for item in low_stock_items],
            'out_of_stock_items': [{
                'id': item.id,
                'name': item.name,
                'reference_sku': item.reference_sku,
                'category': item.category.name if item.category else None,
                'purchase_price': float(item.prix_achat),
                'selling_price': float(item.prix_vente)
            } for item in out_of_stock_items]
        }
        
        return Response(data)
