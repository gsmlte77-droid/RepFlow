"""
Repairs views for FixSoftRepair
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone

from accounts.models import User
from clients.models import Client
from inventory.models import InventoryItem
from .models import RepairTicket, RepairPart, RepairHistory
from .forms import (
    RepairTicketForm, RepairPartForm, RepairSearchForm,
    StatusUpdateForm, QuickRepairForm
)


def is_admin_or_technician_or_cashier(user):
    """Check if user is admin, technician, or cashier"""
    return user.is_authenticated and user.is_admin() or user.role in [User.Role.TECHNICIAN, User.Role.CASHIER]


@login_required
def repair_list_view(request):
    """List all repair tickets"""
    form = RepairSearchForm(request.GET or None)
    
    tickets = RepairTicket.objects.select_related('client', 'technicien').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        client = form.cleaned_data.get('client')
        technicien = form.cleaned_data.get('technicien')
        statut = form.cleaned_data.get('statut')
        priority = form.cleaned_data.get('priority')
        type_appareil = form.cleaned_data.get('type_appareil')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        is_overdue = form.cleaned_data.get('is_overdue')
        
        if search:
            tickets = tickets.filter(
                Q(ticket_number__icontains=search) |
                Q(appareil__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search) |
                Q(client__company_name__icontains=search) |
                Q(client__telephone__icontains=search) |
                Q(description_panne__icontains=search)
            )
        
        if client:
            tickets = tickets.filter(client=client)
        
        if technicien:
            tickets = tickets.filter(technicien=technicien)
        
        if statut:
            tickets = tickets.filter(statut=statut)
        
        if priority:
            tickets = tickets.filter(priority=priority)
        
        if type_appareil:
            tickets = tickets.filter(type_appareil=type_appareil)
        
        if date_from:
            tickets = tickets.filter(date_depot__date__gte=date_from)
        
        if date_to:
            tickets = tickets.filter(date_depot__date__lte=date_to)
        
        if is_overdue is not None:
            if is_overdue:
                tickets = tickets.filter(
                    date_restitution_prevue__lt=timezone.now().date(),
                    statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
                )
            else:
                tickets = tickets.exclude(
                    date_restitution_prevue__lt=timezone.now().date(),
                    statut__in=[RepairTicket.Status.PENDING, RepairTicket.Status.IN_PROGRESS, RepairTicket.Status.WAITING_PARTS]
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
    
    tickets = tickets.order_by('-date_depot')
    
    return render(request, 'repairs/repair_list.html', {
        'tickets': tickets,
        'form': form
    })


@login_required
def repair_detail_view(request, pk):
    """View repair ticket details"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    parts = RepairPart.objects.filter(repair_ticket=ticket).select_related('inventory_item')
    history = RepairHistory.objects.filter(repair_ticket=ticket).order_by('-date_created')
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to view this repair ticket.'))
            return redirect('repairs:repair_list')
    
    return render(request, 'repairs/repair_detail.html', {
        'ticket': ticket,
        'parts': parts,
        'history': history
    })


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def repair_create_view(request):
    """Create new repair ticket"""
    if request.method == 'POST':
        form = RepairTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, _('Repair ticket created successfully!'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    else:
        form = RepairTicketForm()
    
    return render(request, 'repairs/repair_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def repair_update_view(request, pk):
    """Update repair ticket"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to edit this repair ticket.'))
            return redirect('repairs:repair_list')
    
    if request.method == 'POST':
        form = RepairTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, _('Repair ticket updated successfully!'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    else:
        form = RepairTicketForm(instance=ticket)
    
    return render(request, 'repairs/repair_form.html', {
        'form': form,
        'ticket': ticket
    })


@login_required
def repair_status_update_view(request, pk):
    """Update repair ticket status"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to update this repair ticket status.'))
            return redirect('repairs:repair_list')
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            old_status = ticket.statut
            new_status = form.cleaned_data['statut']
            
            # Update status
            ticket.statut = new_status
            ticket.save()
            
            # Add to history
            RepairHistory.objects.create(
                repair_ticket=ticket,
                action=RepairHistory.Action.STATUS_CHANGED,
                old_value=old_status,
                new_value=new_status,
                notes=form.cleaned_data.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, _('Repair ticket status updated successfully!'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    else:
        form = StatusUpdateForm(instance=ticket)
    
    return render(request, 'repairs/repair_status.html', {
        'form': form,
        'ticket': ticket
    })


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def repair_delete_view(request, pk):
    """Delete repair ticket"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to delete this repair ticket.'))
            return redirect('repairs:repair_list')
    
    if request.method == 'POST':
        # Don't actually delete, just cancel
        ticket.statut = RepairTicket.Status.CANCELLED
        ticket.save()
        
        # Add to history
        RepairHistory.objects.create(
            repair_ticket=ticket,
            action=RepairHistory.Action.CANCELLED,
            notes=_('Ticket cancelled by {}').format(request.user.username),
            created_by=request.user
        )
        
        messages.success(request, _('Repair ticket cancelled successfully!'))
        return redirect('repairs:repair_list')
    
    return render(request, 'repairs/repair_confirm_delete.html', {'ticket': ticket})


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def add_part_view(request, repair_pk):
    """Add part to repair ticket"""
    ticket = get_object_or_404(RepairTicket, pk=repair_pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to add parts to this repair ticket.'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        form = RepairPartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.repair_ticket = ticket
            
            # If inventory item is selected, use its price
            if part.inventory_item:
                part.unit_price = part.inventory_item.prix_vente
                part.name = part.inventory_item.name
            
            part.save()
            
            # Update inventory stock if inventory item is selected
            if part.inventory_item and part.inventory_item.is_serialized:
                # For serialized items, don't auto-decrement
                pass
            elif part.inventory_item:
                try:
                    part.inventory_item.update_stock(part.quantity, 'subtract')
                except ValueError as e:
                    messages.error(request, str(e))
                    part.delete()
                    return redirect('repairs:repair_detail', pk=ticket.pk)
            
            messages.success(request, _('Part added successfully!'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    else:
        form = RepairPartForm(initial={'repair_ticket': ticket})
    
    return render(request, 'repairs/repair_part_form.html', {
        'form': form,
        'ticket': ticket
    })


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def update_part_view(request, part_pk):
    """Update part in repair ticket"""
    part = get_object_or_404(RepairPart, pk=part_pk)
    ticket = part.repair_ticket
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to edit parts in this repair ticket.'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        form = RepairPartForm(request.POST, instance=part)
        if form.is_valid():
            old_quantity = part.quantity
            old_inventory_item = part.inventory_item
            
            part = form.save(commit=False)
            part.repair_ticket = ticket
            
            if part.inventory_item:
                part.unit_price = part.inventory_item.prix_vente
                part.name = part.inventory_item.name
            
            part.save()
            
            # Update inventory if quantity changed
            if old_inventory_item and old_inventory_item == part.inventory_item:
                if part.quantity > old_quantity:
                    # Added more quantity
                    try:
                        part.inventory_item.update_stock(part.quantity - old_quantity, 'subtract')
                    except ValueError as e:
                        messages.error(request, str(e))
                elif part.quantity < old_quantity:
                    # Reduced quantity
                    part.inventory_item.update_stock(old_quantity - part.quantity, 'add')
            
            messages.success(request, _('Part updated successfully!'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    else:
        form = RepairPartForm(instance=part)
    
    return render(request, 'repairs/repair_part_form.html', {
        'form': form,
        'ticket': ticket,
        'part': part
    })


@login_required
@user_passes_test(is_admin_or_technician_or_cashier)
def remove_part_view(request, part_pk):
    """Remove part from repair ticket"""
    part = get_object_or_404(RepairPart, pk=part_pk)
    ticket = part.repair_ticket
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            messages.error(request, _('You do not have permission to remove parts from this repair ticket.'))
            return redirect('repairs:repair_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        # Return inventory to stock
        if part.inventory_item:
            part.inventory_item.update_stock(part.quantity, 'add')
        
        part.delete()
        messages.success(request, _('Part removed successfully!'))
        return redirect('repairs:repair_detail', pk=ticket.pk)
    
    return render(request, 'repairs/repair_part_confirm_remove.html', {
        'part': part,
        'ticket': ticket
    })


# AJAX Views
@login_required
def search_repairs(request):
    """Search repair tickets via AJAX"""
    search_term = request.GET.get('search', '')
    limit = int(request.GET.get('limit', 10))
    
    tickets = RepairTicket.objects.select_related('client', 'technicien').filter(is_active=True)
    
    # Apply user permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN:
            tickets = tickets.filter(technicien=request.user)
        elif request.user.role == User.Role.CASHIER:
            tickets = tickets.filter(
                Q(statut=RepairTicket.Status.READY) |
                Q(statut=RepairTicket.Status.DELIVERED)
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
    
    data = [{
        'id': ticket.id,
        'ticket_number': ticket.ticket_number,
        'client_name': ticket.client.get_display_name(),
        'client_telephone': ticket.client.telephone,
        'device': ticket.get_device_info(),
        'statut': ticket.statut,
        'statut_display': ticket.get_statut_display(),
        'priority': ticket.priority,
        'priority_display': ticket.get_priority_display(),
        'date_depot': ticket.date_depot.strftime('%Y-%m-%d %H:%M') if ticket.date_depot else None,
        'date_restitution_prevue': ticket.date_restitution_prevue.strftime('%Y-%m-%d') if ticket.date_restitution_prevue else None,
        'cout_total': float(ticket.cout_total),
        'amount_paid': float(ticket.amount_paid),
        'balance_due': float(ticket.get_balance_due()),
        'is_overdue': ticket.is_overdue()
    } for ticket in tickets]
    
    return JsonResponse(data, safe=False)


@login_required
def get_repair(request, pk):
    """Get repair ticket details via AJAX"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = {
        'id': ticket.id,
        'ticket_number': ticket.ticket_number,
        'client': {
            'id': ticket.client.id,
            'name': ticket.client.get_display_name(),
            'telephone': ticket.client.telephone,
            'email': ticket.client.email
        },
        'device': {
            'appareil': ticket.appareil,
            'type': ticket.type_appareil,
            'brand': ticket.brand,
            'model': ticket.model,
            'serial_number': ticket.serial_number,
            'condition': ticket.device_condition
        },
        'statut': ticket.statut,
        'statut_display': ticket.get_statut_display(),
        'priority': ticket.priority,
        'priority_display': ticket.get_priority_display(),
        'technicien': {
            'id': ticket.technicien.id if ticket.technicien else None,
            'name': ticket.technicien.get_full_name() if ticket.technicien else None
        },
        'dates': {
            'date_depot': ticket.date_depot.strftime('%Y-%m-%d %H:%M') if ticket.date_depot else None,
            'date_restitution_prevue': ticket.date_restitution_prevue.strftime('%Y-%m-%d') if ticket.date_restitution_prevue else None,
            'date_restitution': ticket.date_restitution.strftime('%Y-%m-%d %H:%M') if ticket.date_restitution else None,
            'date_completed': ticket.date_completed.strftime('%Y-%m-%d %H:%M') if ticket.date_completed else None
        },
        'financial': {
            'cout_main_oeuvre': float(ticket.cout_main_oeuvre),
            'cout_pieces': float(ticket.cout_pieces),
            'cout_total': float(ticket.cout_total),
            'discount': float(ticket.discount),
            'amount_paid': float(ticket.amount_paid),
            'balance_due': float(ticket.get_balance_due()),
            'is_paid': ticket.is_paid()
        },
        'description_panne': ticket.description_panne,
        'diagnosis': ticket.diagnosis,
        'repair_notes': ticket.repair_notes,
        'internal_notes': ticket.internal_notes,
        'warranty_months': ticket.warranty_months,
        'warranty_notes': ticket.warranty_notes,
        'accessories': ticket.accessories,
        'is_under_warranty': ticket.is_under_warranty,
        'is_insured': ticket.is_insured,
        'requires_approval': ticket.requires_approval,
        'is_overdue': ticket.is_overdue()
    }
    
    return JsonResponse(data)


@login_required
def update_repair_status(request, pk):
    """Update repair ticket status via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if not new_status:
            return JsonResponse({'error': 'Status is required'}, status=400)
        
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
        
        return JsonResponse({
            'success': True,
            'new_status': ticket.statut,
            'new_status_display': ticket.get_statut_display()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_repair_stats(request):
    """Get repair statistics via AJAX"""
    # Apply user permissions
    tickets = RepairTicket.objects.all()
    
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN:
            tickets = tickets.filter(technicien=request.user)
        elif request.user.role == User.Role.CASHIER:
            tickets = tickets.filter(
                Q(statut=RepairTicket.Status.READY) |
                Q(statut=RepairTicket.Status.DELIVERED)
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
    
    return JsonResponse(stats)


@login_required
def quick_create_repair(request):
    """Quick create repair ticket via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    form = QuickRepairForm(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['client_id']
        client = get_object_or_404(Client, pk=client_id)
        
        ticket = RepairTicket.objects.create(
            client=client,
            appareil=form.cleaned_data['appareil'],
            type_appareil=form.cleaned_data['type_appareil'],
            description_panne=form.cleaned_data['description_panne'],
            priority=form.cleaned_data['priority'],
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'device': ticket.appareil
            }
        })
    else:
        errors = {field: str(error[0]) for field, error in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)


@login_required
def get_repair_history(request, pk):
    """Get repair ticket history via AJAX"""
    ticket = get_object_or_404(RepairTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.TECHNICIAN and ticket.technicien != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    history = RepairHistory.objects.filter(repair_ticket=ticket).select_related('created_by').order_by('-date_created')
    
    data = [{
        'id': h.id,
        'action': h.get_action_display(),
        'old_value': h.old_value,
        'new_value': h.new_value,
        'notes': h.notes,
        'created_by': h.created_by.get_full_name() if h.created_by else None,
        'date_created': h.date_created.strftime('%Y-%m-%d %H:%M:%S') if h.date_created else None
    } for h in history]
    
    return JsonResponse(data, safe=False)
