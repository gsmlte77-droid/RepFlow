"""
Dashboard API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'dashboard_api'

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.DashboardStatsView.as_view(), name='stats'),
    path('repairs/', views.DashboardRepairsView.as_view(), name='repairs'),
    path('financial/', views.DashboardFinancialView.as_view(), name='financial'),
    path('inventory/', views.DashboardInventoryView.as_view(), name='inventory'),
]
