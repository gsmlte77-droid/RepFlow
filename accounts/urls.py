"""
Accounts URLs for FixSoftRepair
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', views.password_change_view, name='password_change'),
    
    # User management (admin only)
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update_view, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete_view, name='user_delete'),
    
    # API endpoints
    path('api/check-username/', views.check_username_availability, name='check_username'),
]
