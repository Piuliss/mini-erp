from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseInvoice
from .serializers import (
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    PurchaseOrderItemSerializer, PurchaseInvoiceSerializer, PurchaseInvoiceCreateSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing suppliers
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Supplier.objects.all().order_by('-created_at')
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """
        Get all orders for a supplier
        """
        supplier = self.get_object()
        orders = PurchaseOrder.objects.filter(supplier=supplier)
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase orders
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by supplier
        supplier_id = self.request.query_params.get('supplier_id', None)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Search by order number
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(order_number__icontains=search)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def send_to_supplier(self, request, pk=None):
        """
        Send purchase order to supplier
        """
        order = self.get_object()
        if order.status == 'draft':
            order.status = 'sent'
            order.save()
            return Response({'message': 'Order sent to supplier successfully'})
        return Response(
            {'error': 'Order cannot be sent to supplier'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a purchase order
        """
        order = self.get_object()
        if order.status == 'sent':
            order.status = 'confirmed'
            order.save()
            return Response({'message': 'Order confirmed successfully'})
        return Response(
            {'error': 'Order cannot be confirmed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Mark order as received
        """
        order = self.get_object()
        if order.status == 'confirmed':
            order.status = 'received'
            order.delivery_date = timezone.now().date()
            order.save()
            return Response({'message': 'Order marked as received'})
        return Response(
            {'error': 'Order cannot be received'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def purchase_summary(self, request):
        """
        Get purchase summary statistics
        """
        today = timezone.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Total purchases
        total_purchases = PurchaseOrder.objects.filter(status='received').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # This month purchases
        this_month_purchases = PurchaseOrder.objects.filter(
            status='received',
            order_date__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Last month purchases
        last_month_purchases = PurchaseOrder.objects.filter(
            status='received',
            order_date__gte=last_month,
            order_date__lt=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Orders by status
        orders_by_status = PurchaseOrder.objects.values('status').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_purchases': float(total_purchases),
            'this_month_purchases': float(this_month_purchases),
            'last_month_purchases': float(last_month_purchases),
            'orders_by_status': list(orders_by_status)
        })


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase order items
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseOrderItem.objects.all().order_by('-created_at')


class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase invoices
    """
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseInvoice.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseInvoiceCreateSerializer
        return PurchaseInvoiceSerializer

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """
        Record a payment for a purchase invoice
        """
        invoice = self.get_object()
        payment_amount = request.data.get('amount', 0)
        
        if payment_amount <= 0:
            return Response(
                {'error': 'Payment amount must be greater than 0'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.paid_amount += payment_amount
        
        # Update status
        if invoice.paid_amount >= invoice.amount:
            invoice.status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'partial'
        
        invoice.save()
        
        return Response(PurchaseInvoiceSerializer(invoice).data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue purchase invoices
        """
        today = timezone.now().date()
        overdue_invoices = PurchaseInvoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partial']
        )
        serializer = PurchaseInvoiceSerializer(overdue_invoices, many=True)
        return Response(serializer.data)
