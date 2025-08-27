from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone

from .models import Supplier, PurchaseInvoice
from .serializers import (
    SupplierSerializer, PurchaseInvoiceSerializer, PurchaseInvoiceCreateSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing suppliers
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'email', 'contact_person']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase invoices
    """
    queryset = PurchaseInvoice.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'supplier']
    search_fields = ['invoice_number', 'supplier__name']
    ordering_fields = ['invoice_date', 'due_date', 'amount', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseInvoiceCreateSerializer
        return PurchaseInvoiceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by supplier if provided
        supplier_id = self.request.query_params.get('supplier', None)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(invoice_number__icontains=search)
        
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark invoice as paid
        """
        invoice = self.get_object()
        paid_amount = request.data.get('paid_amount', invoice.amount)
        
        invoice.paid_amount = paid_amount
        invoice.update_status()
        
        return Response({
            'message': f'Invoice marked as {invoice.status}',
            'status': invoice.status,
            'paid_amount': float(invoice.paid_amount),
            'balance': float(invoice.balance)
        })

    @action(detail=False, methods=['get'])
    def purchase_summary(self, request):
        """
        Get purchase summary statistics
        """
        today = timezone.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Total purchases
        total_purchases = PurchaseInvoice.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # This month purchases
        this_month_purchases = PurchaseInvoice.objects.filter(
            invoice_date__gte=this_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Last month purchases
        last_month_purchases = PurchaseInvoice.objects.filter(
            invoice_date__gte=last_month,
            invoice_date__lt=this_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Invoices by status
        invoices_by_status = PurchaseInvoice.objects.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Outstanding invoices
        outstanding_invoices = PurchaseInvoice.objects.filter(
            status__in=['pending', 'partial']
        ).aggregate(
            count=Count('id'),
            total_amount=Sum('amount'),
            total_paid=Sum('paid_amount')
        )
        
        return Response({
            'total_purchases': float(total_purchases),
            'this_month_purchases': float(this_month_purchases),
            'last_month_purchases': float(last_month_purchases),
            'invoices_by_status': list(invoices_by_status),
            'outstanding_invoices': {
                'count': outstanding_invoices['count'] or 0,
                'total_amount': float(outstanding_invoices['total_amount'] or 0),
                'total_paid': float(outstanding_invoices['total_paid'] or 0)
            }
        })
