"""
Clients URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Client list and management
    path('', views.client_list_view, name='client_list'),
    path('create/', views.client_create_view, name='client_create'),
    path('<int:pk>/', views.client_detail_view, name='client_detail'),
    path('<int:pk>/edit/', views.client_update_view, name='client_update'),
    path('<int:pk>/delete/', views.client_delete_view, name='client_delete'),
    
    # AJAX endpoints
    path('api/search/', views.search_clients, name='search_clients'),
    path('api/<int:pk>/', views.get_client, name='get_client'),
    path('api/<int:pk>/balance/', views.get_client_balance, name='get_client_balance'),
    path('api/<int:pk>/balance/update/', views.update_client_balance, name='update_client_balance'),
    path('api/quick-add/', views.quick_add_client, name='quick_add_client'),
]
