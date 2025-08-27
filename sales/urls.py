from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SaleOrderViewSet, SaleOrderItemViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'orders', SaleOrderViewSet)
router.register(r'order-items', SaleOrderItemViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
