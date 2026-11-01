"""
Accounts API URLs
"""
from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'accounts_api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('check-username/', views.CheckUsernameView.as_view(), name='check_username'),
]
