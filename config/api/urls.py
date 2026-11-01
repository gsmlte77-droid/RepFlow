"""
Config API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'config_api'

router = routers.DefaultRouter()
router.register(r'config', views.AppConfigViewSet, basename='config')

urlpatterns = [
    path('', include(router.urls)),
]
