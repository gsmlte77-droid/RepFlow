"""
Staff URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Staff list and management
    path('', views.staff_list_view, name='staff_list'),
    path('create/', views.staff_create_view, name='staff_create'),
    path('<int:pk>/', views.staff_profile_view, name='staff_profile'),
    path('<int:pk>/edit/', views.staff_update_view, name='staff_update'),
    path('<int:pk>/delete/', views.staff_delete_view, name='staff_delete'),
    
    # AJAX endpoints
    path('api/department/<str:department>/', views.get_staff_by_department, name='get_staff_by_department'),
    path('api/stats/', views.get_staff_stats, name='get_staff_stats'),
]
