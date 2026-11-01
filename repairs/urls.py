"""
Repairs URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'repairs'

urlpatterns = [
    # Repair list and management
    path('', views.repair_list_view, name='repair_list'),
    path('create/', views.repair_create_view, name='repair_create'),
    path('<int:pk>/', views.repair_detail_view, name='repair_detail'),
    path('<int:pk>/edit/', views.repair_update_view, name='repair_update'),
    path('<int:pk>/status/', views.repair_status_update_view, name='repair_status'),
    path('<int:pk>/delete/', views.repair_delete_view, name='repair_delete'),
    
    # Parts management
    path('<int:repair_pk>/parts/add/', views.add_part_view, name='add_part'),
    path('<int:part_pk>/parts/edit/', views.update_part_view, name='update_part'),
    path('<int:part_pk>/parts/remove/', views.remove_part_view, name='remove_part'),
    
    # AJAX endpoints
    path('api/search/', views.search_repairs, name='search_repairs'),
    path('api/<int:pk>/', views.get_repair, name='get_repair'),
    path('api/<int:pk>/status/', views.update_repair_status, name='update_repair_status'),
    path('api/stats/', views.get_repair_stats, name='get_repair_stats'),
    path('api/quick-create/', views.quick_create_repair, name='quick_create_repair'),
    path('api/<int:pk>/history/', views.get_repair_history, name='get_repair_history'),
]
