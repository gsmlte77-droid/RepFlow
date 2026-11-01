"""
Billing views for FixSoftRepair
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone

from accounts.models import User
from clients.models import Client
from repairs.models import RepairTicket
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm, InvoiceSearchForm, PaymentSearchForm


def is_admin_or_cashier(user):
    """Check if user is admin or cashier"""
    return user.is_authenticated and (user.is_admin() or user.role == User.Role.CASHIER)


@login_required
def invoice_list_view(request):
    """List all invoices"""
    form = InvoiceSearchForm(request.GET or None)
    
    invoices = Invoice.objects.select_related('client', 'repair_ticket', 'created_by').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        client = form.cleaned_data.get('client')
        statut = form.cleaned_data.get('statut')
        statut_credit = form.cleaned_data.get('statut_credit')
        invoice_type = form.cleaned_data.get('invoice_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        is_overdue = form.cleaned_data.get('is_overdue')
        
        if search:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search) |
                Q(reference__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search) |
                Q(client__company_name__icontains=search)
            )
        
        if client:
            invoices = invoices.filter(client=client)
        
        if statut:
            invoices = invoices.filter(statut=statut)
        
        if statut_credit:
            invoices = invoices.filter(statut_credit=statut_credit)
        
        if invoice_type:
            invoices = invoices.filter(invoice_type=invoice_type)
        
        if date_from:
            invoices = invoices.filter(invoice_date__gte=date_from)
        
        if date_to:
            invoices = invoices.filter(invoice_date__lte=date_to)
        
        if is_overdue is not None:
            if is_overdue:
                invoices = invoices.filter(
                    due_date__lt=timezone.now().date(),
                    balance_due__gt=0
                )
            else:
                invoices = invoices.exclude(
                    due_date__lt=timezone.now().date(),
                    balance_due__gt=0
                )
    
    # Apply user permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.CASHIER:
            invoices = invoices.filter(
                Q(statut__in=[Invoice.Status.PENDING, Invoice.Status.PARTIALLY_PAID, Invoice.Status.SENT]) |
                Q(balance_due__gt=0)
            )
    
    invoices = invoices.order_by('-invoice_date', '-date_created')
    
    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
        'form': form
    })


@login_required
def invoice_detail_view(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice).order_by('order')
    payments = Payment.objects.filter(invoice=invoice).order_by('-transaction_date')
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.CASHIER and invoice.client != request.user:
            messages.error(request, _('You do not have permission to view this invoice.'))
            return redirect('billing:invoice_list')
    
    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'payments': payments
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def invoice_create_view(request):
    """Create new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, _('Invoice created successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    
    return render(request, 'billing/invoice_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_cashier)
def invoice_update_view(request, pk):
    """Update invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, _('Invoice updated successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
    
    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'invoice': invoice
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def invoice_delete_view(request, pk):
    """Delete invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        # Don't actually delete, just cancel
        invoice.statut = Invoice.Status.CANCELLED
        invoice.save()
        messages.success(request, _('Invoice cancelled successfully!'))
        return redirect('billing:invoice_list')
    
    return render(request, 'billing/invoice_confirm_delete.html', {'invoice': invoice})


@login_required
@user_passes_test(is_admin_or_cashier)
def invoice_send_view(request, pk):
    """Send invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        invoice.statut = Invoice.Status.SENT
        invoice.sent_date = timezone.now()
        invoice.save()
        messages.success(request, _('Invoice sent successfully!'))
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    return render(request, 'billing/invoice_send.html', {'invoice': invoice})


@login_required
@user_passes_test(is_admin_or_cashier)
def add_item_view(request, invoice_pk):
    """Add item to invoice"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            messages.success(request, _('Item added successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm()
    
    return render(request, 'billing/invoice_item_form.html', {
        'form': form,
        'invoice': invoice
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def update_item_view(request, item_pk):
    """Update invoice item"""
    item = get_object_or_404(InvoiceItem, pk=item_pk)
    invoice = item.invoice
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('Item updated successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm(instance=item)
    
    return render(request, 'billing/invoice_item_form.html', {
        'form': form,
        'invoice': invoice,
        'item': item
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def remove_item_view(request, item_pk):
    """Remove item from invoice"""
    item = get_object_or_404(InvoiceItem, pk=item_pk)
    invoice = item.invoice
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, _('Item removed successfully!'))
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    return render(request, 'billing/invoice_item_confirm_remove.html', {
        'item': item,
        'invoice': invoice
    })


@login_required
def payment_list_view(request):
    """List all payments"""
    form = PaymentSearchForm(request.GET or None)
    
    payments = Payment.objects.select_related('invoice', 'invoice__client', 'created_by').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        invoice = form.cleaned_data.get('invoice')
        payment_method = form.cleaned_data.get('payment_method')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            payments = payments.filter(
                Q(invoice__invoice_number__icontains=search) |
                Q(reference__icontains=search) |
                Q(invoice__client__first_name__icontains=search) |
                Q(invoice__client__last_name__icontains=search)
            )
        
        if invoice:
            payments = payments.filter(invoice=invoice)
        
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
        
        if date_from:
            payments = payments.filter(transaction_date__date__gte=date_from)
        
        if date_to:
            payments = payments.filter(transaction_date__date__lte=date_to)
    
    # Apply user permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.CASHIER:
            payments = payments.filter(created_by=request.user)
    
    payments = payments.order_by('-transaction_date')
    
    return render(request, 'billing/payment_list.html', {
        'payments': payments,
        'form': form
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def add_payment_view(request, invoice_pk):
    """Add payment to invoice"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            payment.save()
            messages.success(request, _('Payment added successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = PaymentForm(initial={'invoice': invoice})
    
    return render(request, 'billing/payment_form.html', {
        'form': form,
        'invoice': invoice
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def update_payment_view(request, payment_pk):
    """Update payment"""
    payment = get_object_or_404(Payment, pk=payment_pk)
    invoice = payment.invoice
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, _('Payment updated successfully!'))
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'billing/payment_form.html', {
        'form': form,
        'invoice': invoice,
        'payment': payment
    })


@login_required
@user_passes_test(is_admin_or_cashier)
def remove_payment_view(request, payment_pk):
    """Remove payment"""
    payment = get_object_or_404(Payment, pk=payment_pk)
    invoice = payment.invoice
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, _('Payment removed successfully!'))
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    return render(request, 'billing/payment_confirm_remove.html', {
        'payment': payment,
        'invoice': invoice
    })


# AJAX Views
@login_required
def search_invoices(request):
    """Search invoices via AJAX"""
    search_term = request.GET.get('search', '')
    limit = int(request.GET.get('limit', 10))
    
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
    
    data = [{
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'client_name': invoice.client.get_display_name(),
        'client_telephone': invoice.client.telephone,
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
        'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
        'total': float(invoice.total),
        'amount_paid': float(invoice.amount_paid),
        'balance_due': float(invoice.balance_due),
        'statut': invoice.statut,
        'statut_display': invoice.get_statut_display(),
        'is_overdue': invoice.is_overdue()
    } for invoice in invoices]
    
    return JsonResponse(data, safe=False)


@login_required
def get_invoice(request, pk):
    """Get invoice details via AJAX"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.CASHIER and invoice.client != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    items = InvoiceItem.objects.filter(invoice=invoice).order_by('order')
    payments = Payment.objects.filter(invoice=invoice).order_by('-transaction_date')
    
    data = {
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'client': {
            'id': invoice.client.id,
            'name': invoice.client.get_display_name(),
            'telephone': invoice.client.telephone,
            'email': invoice.client.email,
            'address': invoice.client.get_address()
        },
        'repair_ticket': {
            'id': invoice.repair_ticket.id if invoice.repair_ticket else None,
            'ticket_number': invoice.repair_ticket.ticket_number if invoice.repair_ticket else None
        } if invoice.repair_ticket else None,
        'invoice_type': invoice.invoice_type,
        'invoice_type_display': invoice.get_invoice_type_display(),
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
        'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
        'reference': invoice.reference,
        'statut': invoice.statut,
        'statut_display': invoice.get_statut_display(),
        'statut_credit': invoice.statut_credit,
        'financial': {
            'subtotal': float(invoice.subtotal),
            'tax_rate': float(invoice.tax_rate),
            'tax_amount': float(invoice.tax_amount),
            'discount': float(invoice.discount),
            'total': float(invoice.total),
            'amount_paid': float(invoice.amount_paid),
            'balance_due': float(invoice.balance_due),
            'reste_a_payer': float(invoice.reste_a_payer),
            'is_paid': invoice.is_paid(),
            'is_overdue': invoice.is_overdue(),
            'days_overdue': invoice.get_days_overdue()
        },
        'payment_terms': invoice.payment_terms,
        'notes': invoice.notes,
        'internal_notes': invoice.internal_notes,
        'items': [{
            'id': item.id,
            'description': item.description,
            'quantity': float(item.quantity),
            'unit_price': float(item.unit_price),
            'tax_rate': float(item.tax_rate),
            'total': float(item.total)
        } for item in items],
        'payments': [{
            'id': payment.id,
            'amount': float(payment.amount),
            'payment_method': payment.payment_method,
            'payment_method_display': payment.get_payment_method_display(),
            'reference': payment.reference,
            'transaction_date': payment.transaction_date.strftime('%Y-%m-%d %H:%M') if payment.transaction_date else None,
            'notes': payment.notes
        } for payment in payments]
    }
    
    return JsonResponse(data)


@login_required
def get_invoice_stats(request):
    """Get invoice statistics via AJAX"""
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
    
    return JsonResponse(stats)


@login_required
def update_invoice_status(request, pk):
    """Update invoice status via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        if request.user.role == User.Role.CASHIER:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        new_status = request.POST.get('status')
        
        if not new_status:
            return JsonResponse({'error': 'Status is required'}, status=400)
        
        invoice.statut = new_status
        if new_status == Invoice.Status.SENT:
            invoice.sent_date = timezone.now()
        elif new_status == Invoice.Status.PAID:
            invoice.paid_date = timezone.now()
        invoice.save()
        
        return JsonResponse({
            'success': True,
            'new_status': invoice.statut,
            'new_status_display': invoice.get_statut_display()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_payment_ajax(request):
    """Add payment via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        invoice_id = request.POST.get('invoice_id')
        amount = float(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method', Payment.PaymentMethod.CASH)
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        
        if not invoice_id:
            return JsonResponse({'error': 'Invoice ID is required'}, status=400)
        
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
        
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        # Check permissions
        if not request.user.is_admin():
            if request.user.role == User.Role.CASHIER:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
        payment = Payment.objects.create(
            invoice=invoice,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'payment': {
                'id': payment.id,
                'amount': float(payment.amount),
                'payment_method': payment.payment_method,
                'payment_method_display': payment.get_payment_method_display(),
                'reference': payment.reference,
                'transaction_date': payment.transaction_date.strftime('%Y-%m-%d %H:%M')
            },
            'invoice': {
                'balance_due': float(invoice.balance_due),
                'amount_paid': float(invoice.amount_paid),
                'is_paid': invoice.is_paid()
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_client_invoices(request, client_pk):
    """Get invoices for a client via AJAX"""
    client = get_object_or_404(Client, pk=client_pk)
    
    invoices = Invoice.objects.filter(client=client).select_related('repair_ticket').order_by('-invoice_date')
    
    data = [{
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
        'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
        'total': float(invoice.total),
        'amount_paid': float(invoice.amount_paid),
        'balance_due': float(invoice.balance_due),
        'statut': invoice.statut,
        'statut_display': invoice.get_statut_display(),
        'repair_ticket': {
            'id': invoice.repair_ticket.id if invoice.repair_ticket else None,
            'ticket_number': invoice.repair_ticket.ticket_number if invoice.repair_ticket else None
        } if invoice.repair_ticket else None
    } for invoice in invoices]
    
    return JsonResponse(data, safe=False)


@login_required
def get_client_balance(request, client_pk):
    """Get client balance via AJAX"""
    client = get_object_or_404(Client, pk=client_pk)
    
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
    
    return JsonResponse(data)
