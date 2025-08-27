from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseInvoiceViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'invoices', PurchaseInvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
