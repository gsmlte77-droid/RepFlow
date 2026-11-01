"""
Dashboard views for FixSoftRepair
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from django.utils import timezone

from repairs.models import RepairTicket
from clients.models import Client
from inventory.models import InventoryItem
from billing.models import Invoice, Payment
from config.models import AppConfig


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    config = AppConfig.get_instance()
    
    # Get statistics based on user role
    if request.user.is_admin():
        # Admin sees all data
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
        
        recent_repairs = RepairTicket.objects.select_related('client', 'technicien').order_by('-date_depot')[:10]
        recent_invoices = Invoice.objects.select_related('client').order_by('-invoice_date')[:10]
        
        # Charts data
        repairs_by_status = list(RepairTicket.objects.values('statut').annotate(count=Count('id')).order_by('statut'))
        repairs_by_device = list(RepairTicket.objects.values('type_appareil').annotate(count=Count('id')).order_by('type_appareil'))
        revenue_by_month = list(Invoice.objects.extra(
            {'month': "strftime('%Y-%m', invoice_date)"}
        ).values('month').annotate(total=Sum('total')).order_by('month'))
        
    elif request.user.role == User.Role.TECHNICIAN:
        # Technician sees only their repairs
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
        
        recent_repairs = RepairTicket.objects.filter(
            technicien=request.user
        ).select_related('client').order_by('-date_depot')[:10]
        recent_invoices = []
        
        # Charts data
        repairs_by_status = list(RepairTicket.objects.filter(
            technicien=request.user
        ).values('statut').annotate(count=Count('id')).order_by('statut'))
        repairs_by_device = list(RepairTicket.objects.filter(
            technicien=request.user
        ).values('type_appareil').annotate(count=Count('id')).order_by('type_appareil'))
        revenue_by_month = []
        
    elif request.user.role == User.Role.CASHIER:
        # Cashier sees financial data
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
        
        recent_repairs = []
        recent_invoices = Invoice.objects.select_related('client').order_by('-invoice_date')[:10]
        
        # Charts data
        repairs_by_status = list(RepairTicket.objects.values('statut').annotate(count=Count('id')).order_by('statut'))
        repairs_by_device = list(RepairTicket.objects.values('type_appareil').annotate(count=Count('id')).order_by('type_appareil'))
        revenue_by_month = list(Invoice.objects.extra(
            {'month': "strftime('%Y-%m', invoice_date)"}
        ).values('month').annotate(total=Sum('total')).order_by('month'))
    else:
        # Default for other roles
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
        
        recent_repairs = []
        recent_invoices = []
        
        repairs_by_status = []
        repairs_by_device = []
        revenue_by_month = []
    
    context = {
        'config': config,
        'stats': {
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
        },
        'recent_repairs': recent_repairs,
        'recent_invoices': recent_invoices,
        'charts': {
            'repairs_by_status': repairs_by_status,
            'repairs_by_device': repairs_by_device,
            'revenue_by_month': revenue_by_month,
        }
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def get_dashboard_stats(request):
    """Get dashboard statistics via AJAX"""
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
    
    return JsonResponse(stats)
