"""
URL configuration for FixSoftRepair project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers

# API Router
api_router = routers.DefaultRouter()

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # i18n JavaScript catalog
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    
    # API v1
    path('api/v1/', include([
        # Authentication
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
        # Accounts
        path('accounts/', include('accounts.api.urls')),
        
        # Staff
        path('staff/', include('staff.api.urls')),
        
        # Config
        path('config/', include('config.api.urls')),
        
        # Clients
        path('clients/', include('clients.api.urls')),
        
        # Inventory
        path('inventory/', include('inventory.api.urls')),
        
        # Repairs
        path('repairs/', include('repairs.api.urls')),
        
        # Billing
        path('billing/', include('billing.api.urls')),
        
        # Dashboard
        path('dashboard/', include('dashboard.api.urls')),
    ])),
    
    # Language switch
    path('language/', include('django.conf.urls.i18n')),
]

# Main app URLs with i18n
urlpatterns += i18n_patterns(
    # Accounts
    path('accounts/', include('accounts.urls')),
    
    # Staff
    path('staff/', include('staff.urls')),
    
    # Config
    path('config/', include('config.urls')),
    
    # Clients
    path('clients/', include('clients.urls')),
    
    # Inventory
    path('inventory/', include('inventory.urls')),
    
    # Repairs
    path('repairs/', include('repairs.urls')),
    
    # Billing
    path('billing/', include('billing.urls')),
    
    # Dashboard
    path('', include('dashboard.urls')),
)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add API root URL
urlpatterns += [
    path('api/v1/', include(api_router.urls)),
]
