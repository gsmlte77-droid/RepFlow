"""
Staff API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'staff_api'

router = routers.DefaultRouter()
router.register(r'staff', views.StaffMemberViewSet, basename='staff')

urlpatterns = [
    path('', include(router.urls)),
    path('department/<str:department>/', views.StaffByDepartmentView.as_view(), name='by_department'),
    path('stats/', views.StaffStatsView.as_view(), name='stats'),
]
