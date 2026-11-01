"""
Inventory URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Categories
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_view, name='category_update'),
    
    # Suppliers
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/create/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update_view, name='supplier_update'),
    
    # Inventory
    path('', views.inventory_list_view, name='inventory_list'),
    path('create/', views.inventory_create_view, name='inventory_create'),
    path('<int:pk>/', views.inventory_detail_view, name='inventory_detail'),
    path('<int:pk>/edit/', views.inventory_update_view, name='inventory_update'),
    
    # Stock management
    path('stock/adjust/', views.stock_adjustment_view, name='stock_adjustment'),
    
    # AJAX endpoints
    path('api/search/', views.search_inventory, name='search_inventory'),
    path('api/<int:pk>/', views.get_item, name='get_item'),
    path('api/<int:pk>/stock/', views.update_stock, name='update_stock'),
    path('api/low-stock/', views.get_low_stock_items, name='get_low_stock_items'),
    path('api/stats/', views.get_stock_stats, name='get_stock_stats'),
]
