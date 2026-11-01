"""
Inventory API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'inventory_api'

router = routers.DefaultRouter()
router.register(r'items', views.InventoryItemViewSet, basename='item')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'stock-movements', views.StockMovementViewSet, basename='stock_movement')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.InventorySearchView.as_view(), name='search'),
    path('low-stock/', views.LowStockView.as_view(), name='low_stock'),
    path('stats/', views.InventoryStatsView.as_view(), name='stats'),
    path('<int:pk>/stock/', views.ItemStockView.as_view(), name='item_stock'),
]
