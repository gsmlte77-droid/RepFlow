"""
Clients API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'clients_api'

router = routers.DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.ClientSearchView.as_view(), name='search'),
    path('<int:pk>/balance/', views.ClientBalanceView.as_view(), name='balance'),
    path('quick-add/', views.QuickClientView.as_view(), name='quick_add'),
]
