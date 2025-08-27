"""
URL configuration for mini_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Mini ERP API",
        default_version='v1',
        description="""
        # Mini ERP API Documentation
        
        This is a comprehensive ERP system API built with Django REST Framework.
        
        ## Features:
        - **Authentication**: JWT-based authentication
        - **Users & Roles**: User management with role-based permissions
        - **Inventory**: Product and stock management
        - **Sales**: Customer orders and invoicing
        - **Purchases**: Supplier orders and procurement
        - **Reports**: Comprehensive reporting system
        
        ## Authentication:
        All endpoints require authentication except for login and register.
        Include the JWT token in the Authorization header:
        ```
        Authorization: Bearer <your_token>
        ```
        
        ## Getting Started:
        1. Register a new user: `POST /api/users/register/`
        2. Login to get tokens: `POST /api/users/login/`
        3. Use the access token for API requests
        
        ## Sample Data:
        The system comes with sample data for testing:
        - Users with different roles
        - Products and categories
        - Customers and suppliers
        - Sample orders and invoices
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@minierp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/users/', include('users.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/reports/', include('reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
