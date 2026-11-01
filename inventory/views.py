"""
Inventory views for FixSoftRepair
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import User
from .models import InventoryItem, Category, Supplier, StockMovement
from .forms import (
    InventoryItemForm, CategoryForm, SupplierForm,
    InventorySearchForm, StockAdjustmentForm, QuickStockForm
)


def is_admin_or_technician(user):
    """Check if user is admin or technician"""
    return user.is_authenticated and (user.is_admin() or user.role == User.Role.TECHNICIAN)


@login_required
def category_list_view(request):
    """List all categories"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin_or_technician)
def category_create_view(request):
    """Create new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category created successfully!'))
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'inventory/category_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_technician)
def category_update_view(request, pk):
    """Update category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category updated successfully!'))
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'category': category
    })


@login_required
def supplier_list_view(request):
    """List all suppliers"""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


@login_required
@user_passes_test(is_admin_or_technician)
def supplier_create_view(request):
    """Create new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Supplier created successfully!'))
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_technician)
def supplier_update_view(request, pk):
    """Update supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, _('Supplier updated successfully!'))
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'supplier': supplier
    })


@login_required
def inventory_list_view(request):
    """List all inventory items"""
    form = InventorySearchForm(request.GET or None)
    
    items = InventoryItem.objects.select_related('category', 'supplier').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        supplier = form.cleaned_data.get('supplier')
        item_type = form.cleaned_data.get('item_type')
        stock_status = form.cleaned_data.get('stock_status')
        is_active = form.cleaned_data.get('is_active')
        
        if search:
            items = items.filter(
                Q(name__icontains=search) |
                Q(reference_sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(description__icontains=search)
            )
        
        if category:
            items = items.filter(category=category)
        
        if supplier:
            items = items.filter(supplier=supplier)
        
        if item_type:
            items = items.filter(item_type=item_type)
        
        if stock_status:
            # Filter by stock status
            if stock_status == 'IN_STOCK':
                items = items.filter(quantite_stock__gt=0)
            elif stock_status == 'OUT_OF_STOCK':
                items = items.filter(quantite_stock=0)
            elif stock_status == 'LOW_STOCK':
                from config.models import AppConfig
                config = AppConfig.get_instance()
                threshold = config.low_stock_threshold
                items = items.filter(
                    quantite_stock__gt=0,
                    quantite_stock__lte=threshold
                )
        
        if is_active is not None:
            items = items.filter(is_active=is_active)
    
    items = items.order_by('name')
    
    return render(request, 'inventory/inventory_list.html', {
        'items': items,
        'form': form
    })


@login_required
def inventory_detail_view(request, pk):
    """View inventory item details"""
    item = get_object_or_404(InventoryItem, pk=pk)
    stock_movements = StockMovement.objects.filter(item=item).order_by('-date_created')[:20]
    
    return render(request, 'inventory/inventory_detail.html', {
        'item': item,
        'stock_movements': stock_movements
    })


@login_required
@user_passes_test(is_admin_or_technician)
def inventory_create_view(request):
    """Create new inventory item"""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Inventory item created successfully!'))
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm()
    
    return render(request, 'inventory/inventory_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_technician)
def inventory_update_view(request, pk):
    """Update inventory item"""
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('Inventory item updated successfully!'))
            return redirect('inventory:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    
    return render(request, 'inventory/inventory_form.html', {
        'form': form,
        'item': item
    })


@login_required
@user_passes_test(is_admin_or_technician)
def stock_adjustment_view(request):
    """Stock adjustment view"""
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()
            messages.success(request, _('Stock adjusted successfully!'))
            return redirect('inventory:inventory_list')
    else:
        form = StockAdjustmentForm()
    
    return render(request, 'inventory/stock_adjustment.html', {'form': form})


# AJAX Views
@login_required
def search_inventory(request):
    """Search inventory items via AJAX"""
    search_term = request.GET.get('search', '')
    limit = int(request.GET.get('limit', 10))
    
    items = InventoryItem.objects.filter(is_active=True)
    
    if search_term:
        items = items.filter(
            Q(name__icontains=search_term) |
            Q(reference_sku__icontains=search_term) |
            Q(barcode__icontains=search_term)
        )
    
    items = items.order_by('name')[:limit]
    
    data = [{
        'id': item.id,
        'name': item.name,
        'reference_sku': item.reference_sku,
        'barcode': item.barcode,
        'stock': item.quantite_stock,
        'stock_status': item.get_stock_status_display(),
        'price': float(item.prix_vente),
        'category': item.category.name if item.category else None
    } for item in items]
    
    return JsonResponse(data, safe=False)


@login_required
def get_item(request, pk):
    """Get inventory item details via AJAX"""
    item = get_object_or_404(InventoryItem, pk=pk)
    
    data = {
        'id': item.id,
        'name': item.name,
        'reference_sku': item.reference_sku,
        'barcode': item.barcode,
        'description': item.description,
        'stock': item.quantite_stock,
        'alert_threshold': item.seuil_alerte,
        'stock_status': item.get_stock_status(),
        'purchase_price': float(item.prix_achat),
        'selling_price': float(item.prix_vente),
        'category': item.category.id if item.category else None,
        'category_name': item.category.name if item.category else None,
        'supplier': item.supplier.id if item.supplier else None,
        'supplier_name': item.supplier.name if item.supplier else None,
        'location': item.location,
        'is_active': item.is_active,
        'can_be_sold': item.can_be_sold(),
        'profit_margin': float(item.get_profit_margin())
    }
    
    return JsonResponse(data)


@login_required
def update_stock(request, pk):
    """Update inventory item stock via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    item = get_object_or_404(InventoryItem, pk=pk)
    
    try:
        quantity = int(request.POST.get('quantity', 0))
        operation = request.POST.get('operation', 'add')
        notes = request.POST.get('notes', '')
        
        if operation == 'add':
            new_stock = item.update_stock(quantity, 'add')
        elif operation == 'subtract':
            new_stock = item.update_stock(quantity, 'subtract')
            # Create stock movement
            StockMovement.objects.create(
                item=item,
                movement_type=StockMovement.MovementType.SALE,
                quantity=quantity,
                quantity_before=item.quantite_stock + quantity,
                quantity_after=new_stock,
                reference=f"AJAX-{request.user.username}",
                notes=notes,
                created_by=request.user
            )
        else:
            return JsonResponse({'error': 'Invalid operation'}, status=400)
        
        return JsonResponse({
            'success': True,
            'new_stock': new_stock,
            'stock_status': item.get_stock_status_display()
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_low_stock_items(request):
    """Get low stock items via AJAX"""
    from config.models import AppConfig
    config = AppConfig.get_instance()
    threshold = config.low_stock_threshold
    
    items = InventoryItem.objects.filter(
        is_active=True,
        quantite_stock__gt=0,
        quantite_stock__lte=threshold
    ).select_related('category')
    
    data = [{
        'id': item.id,
        'name': item.name,
        'reference_sku': item.reference_sku,
        'stock': item.quantite_stock,
        'alert_threshold': item.seuil_alerte,
        'category': item.category.name if item.category else None
    } for item in items]
    
    return JsonResponse(data, safe=False)


@login_required
def get_stock_stats(request):
    """Get inventory statistics via AJAX"""
    from django.db.models import Sum, Count
    from config.models import AppConfig
    
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
    
    return JsonResponse(stats)
