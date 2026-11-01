"""
Config URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'config'

urlpatterns = [
    # Main config view
    path('', views.config_view, name='config'),
    
    # AJAX endpoints
    path('api/get/', views.get_config, name='get_config'),
    path('api/update/', views.update_config, name='update_config'),
]
