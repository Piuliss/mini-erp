from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseOrderViewSet, PurchaseOrderItemViewSet, PurchaseInvoiceViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'orders', PurchaseOrderViewSet)
router.register(r'order-items', PurchaseOrderItemViewSet)
router.register(r'invoices', PurchaseInvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
