"""
Billing API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'billing_api'

router = routers.DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'invoice-items', views.InvoiceItemViewSet, basename='invoice_item')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('invoices/search/', views.InvoiceSearchView.as_view(), name='invoice_search'),
    path('invoices/stats/', views.InvoiceStatsView.as_view(), name='invoice_stats'),
    path('invoices/<int:pk>/status/', views.InvoiceStatusView.as_view(), name='invoice_status'),
    path('invoices/<int:pk>/send/', views.InvoiceSendView.as_view(), name='invoice_send'),
    path('invoices/<int:pk>/items/', views.InvoiceItemsView.as_view(), name='invoice_items'),
    path('invoices/<int:pk>/payments/', views.InvoicePaymentsView.as_view(), name='invoice_payments'),
    path('clients/<int:client_pk>/invoices/', views.ClientInvoicesView.as_view(), name='client_invoices'),
    path('clients/<int:client_pk>/balance/', views.ClientBalanceView.as_view(), name='client_balance'),
]
