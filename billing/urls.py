"""
Billing URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Invoices
    path('invoices/', views.invoice_list_view, name='invoice_list'),
    path('invoices/create/', views.invoice_create_view, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_update_view, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete_view, name='invoice_delete'),
    path('invoices/<int:pk>/send/', views.invoice_send_view, name='invoice_send'),
    
    # Invoice items
    path('invoices/<int:invoice_pk>/items/add/', views.add_item_view, name='add_item'),
    path('invoices/items/<int:item_pk>/edit/', views.update_item_view, name='update_item'),
    path('invoices/items/<int:item_pk>/remove/', views.remove_item_view, name='remove_item'),
    
    # Payments
    path('payments/', views.payment_list_view, name='payment_list'),
    path('invoices/<int:invoice_pk>/payments/add/', views.add_payment_view, name='add_payment'),
    path('payments/<int:payment_pk>/edit/', views.update_payment_view, name='update_payment'),
    path('payments/<int:payment_pk>/remove/', views.remove_payment_view, name='remove_payment'),
    
    # AJAX endpoints
    path('api/invoices/search/', views.search_invoices, name='search_invoices'),
    path('api/invoices/<int:pk>/', views.get_invoice, name='get_invoice'),
    path('api/invoices/stats/', views.get_invoice_stats, name='get_invoice_stats'),
    path('api/invoices/<int:pk>/status/', views.update_invoice_status, name='update_invoice_status'),
    path('api/payments/add/', views.add_payment_ajax, name='add_payment_ajax'),
    path('api/clients/<int:client_pk>/invoices/', views.get_client_invoices, name='get_client_invoices'),
    path('api/clients/<int:client_pk>/balance/', views.get_client_balance, name='get_client_balance'),
]
