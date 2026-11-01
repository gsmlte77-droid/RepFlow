"""
Repairs API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'repairs_api'

router = routers.DefaultRouter()
router.register(r'tickets', views.RepairTicketViewSet, basename='ticket')
router.register(r'parts', views.RepairPartViewSet, basename='part')
router.register(r'history', views.RepairHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.RepairSearchView.as_view(), name='search'),
    path('stats/', views.RepairStatsView.as_view(), name='stats'),
    path('<int:pk>/status/', views.TicketStatusView.as_view(), name='ticket_status'),
    path('<int:pk>/parts/', views.TicketPartsView.as_view(), name='ticket_parts'),
    path('<int:pk>/history/', views.TicketHistoryView.as_view(), name='ticket_history'),
    path('quick-create/', views.QuickRepairView.as_view(), name='quick_create'),
]
