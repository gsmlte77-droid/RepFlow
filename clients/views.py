"""
Clients views for FixSoftRepair
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import User
from .models import Client
from .forms import ClientForm, ClientSearchForm, QuickClientForm


def is_admin_or_cashier(user):
    """Check if user is admin or cashier"""
    return user.is_authenticated and (user.is_admin() or user.role == User.Role.CASHIER)


@login_required
def client_list_view(request):
    """List all clients"""
    form = ClientSearchForm(request.GET or None)
    
    clients = Client.objects.all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        client_type = form.cleaned_data.get('client_type')
        membership_status = form.cleaned_data.get('membership_status')
        is_active = form.cleaned_data.get('is_active')
        has_balance = form.cleaned_data.get('has_balance')
        
        if search:
            clients = clients.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(telephone__icontains=search) |
                Q(email__icontains=search) |
                Q(registration_number__icontains=search)
            )
        
        if client_type:
            clients = clients.filter(client_type=client_type)
        
        if membership_status:
            clients = clients.filter(membership_status=membership_status)
        
        if is_active is not None:
            clients = clients.filter(is_active=is_active)
        
        if has_balance is not None:
            if has_balance:
                clients = clients.exclude(current_balance=0)
            else:
                clients = clients.filter(current_balance=0)
    
    clients = clients.order_by('-date_created')
    
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'form': form
    })


@login_required
def client_detail_view(request, pk):
    """View client details"""
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})


@login_required
@user_passes_test(is_admin_or_cashier)
def client_create_view(request):
    """Create new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, _('Client created successfully!'))
            return redirect('clients:client_list')
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_cashier)
def client_update_view(request, pk):
    """Update client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, _('Client updated successfully!'))
            return redirect('clients:client_list')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def client_delete_view(request, pk):
    """Delete client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        # Don't actually delete, just deactivate
        client.is_active = False
        client.save()
        messages.success(request, _('Client deactivated successfully!'))
        return redirect('clients:client_list')
    
    return render(request, 'clients/client_confirm_delete.html', {'client': client})


# AJAX Views
@login_required
def search_clients(request):
    """Search clients via AJAX"""
    search_term = request.GET.get('search', '')
    limit = int(request.GET.get('limit', 10))
    
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
    
    data = [{
        'id': client.id,
        'name': client.get_display_name(),
        'telephone': client.telephone,
        'email': client.email,
        'address': client.get_address(),
        'balance': float(client.current_balance),
        'client_type': client.get_client_type_display()
    } for client in clients]
    
    return JsonResponse(data, safe=False)


@login_required
def get_client(request, pk):
    """Get client details via AJAX"""
    client = get_object_or_404(Client, pk=pk)
    
    data = {
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'company_name': client.company_name,
        'telephone': client.telephone,
        'secondary_telephone': client.secondary_telephone,
        'email': client.email,
        'address': client.get_address(),
        'current_balance': float(client.current_balance),
        'credit_limit': float(client.credit_limit) if client.credit_limit else None,
        'discount_rate': float(client.discount_rate),
        'membership_status': client.membership_status,
        'is_blacklisted': client.is_blacklisted,
        'client_type': client.client_type
    }
    
    return JsonResponse(data)


@login_required
def get_client_balance(request, pk):
    """Get client balance via AJAX"""
    client = get_object_or_404(Client, pk=pk)
    
    data = {
        'current_balance': float(client.current_balance),
        'credit_limit': float(client.credit_limit) if client.credit_limit else None,
        'can_receive_credit': client.can_receive_credit(),
        'balance_status': client.get_balance_status()
    }
    
    return JsonResponse(data)


@login_required
def update_client_balance(request, pk):
    """Update client balance via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    client = get_object_or_404(Client, pk=pk)
    
    try:
        amount = float(request.POST.get('amount', 0))
        client.current_balance = amount
        client.save()
        return JsonResponse({'success': True, 'new_balance': float(client.current_balance)})
    except ValueError:
        return JsonResponse({'error': 'Invalid amount'}, status=400)


@login_required
def quick_add_client(request):
    """Quick add client via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    form = QuickClientForm(request.POST)
    if form.is_valid():
        client = form.save()
        return JsonResponse({
            'success': True,
            'client': {
                'id': client.id,
                'name': client.get_display_name(),
                'telephone': client.telephone
            }
        })
    else:
        errors = {field: str(error[0]) for field, error in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=400)
