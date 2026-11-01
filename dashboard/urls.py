"""
Dashboard URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_view, name='home'),
    
    # AJAX endpoints
    path('api/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
]
