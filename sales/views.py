from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Customer, SaleOrder, SaleOrderItem, Invoice
from .serializers import (
    CustomerSerializer, SaleOrderSerializer, SaleOrderCreateSerializer,
    SaleOrderItemSerializer, InvoiceSerializer, InvoiceCreateSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-created_at')
        
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
        Get all orders for a customer
        """
        customer = self.get_object()
        orders = SaleOrder.objects.filter(customer=customer)
        serializer = SaleOrderSerializer(orders, many=True)
        return Response(serializer.data)


class SaleOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sale orders
    """
    queryset = SaleOrder.objects.all()
    serializer_class = SaleOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SaleOrder.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Search by order number
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(order_number__icontains=search)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return SaleOrderCreateSerializer
        return SaleOrderSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a sale order
        """
        order = self.get_object()
        try:
            order.confirm()
            return Response({'message': 'Order confirmed successfully'})
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Order cannot be confirmed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """
        Mark order as shipped
        """
        order = self.get_object()
        if order.status == 'confirmed':
            order.status = 'shipped'
            order.save()
            return Response({'message': 'Order marked as shipped'})
        return Response(
            {'error': 'Order cannot be shipped'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """
        Mark order as delivered
        """
        order = self.get_object()
        if order.status == 'shipped':
            order.status = 'delivered'
            order.save()
            return Response({'message': 'Order marked as delivered'})
        return Response(
            {'error': 'Order cannot be delivered'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """
        Get sales summary statistics
        """
        today = timezone.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Total sales
        total_sales = SaleOrder.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # This month sales
        this_month_sales = SaleOrder.objects.filter(
            status='delivered',
            order_date__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Last month sales
        last_month_sales = SaleOrder.objects.filter(
            status='delivered',
            order_date__gte=last_month,
            order_date__lt=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Orders by status
        orders_by_status = SaleOrder.objects.values('status').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_sales': float(total_sales),
            'this_month_sales': float(this_month_sales),
            'last_month_sales': float(last_month_sales),
            'orders_by_status': list(orders_by_status)
        })


class SaleOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sale order items
    """
    queryset = SaleOrderItem.objects.all()
    serializer_class = SaleOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SaleOrderItem.objects.all().order_by('-created_at')


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """
        Record a payment for an invoice
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
        
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue invoices
        """
        today = timezone.now().date()
        overdue_invoices = Invoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partial']
        )
        serializer = InvoiceSerializer(overdue_invoices, many=True)
        return Response(serializer.data)
