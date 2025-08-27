from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta, datetime
from users.models import User
from inventory.models import Product, Category, StockMovement
from sales.models import SaleOrder, Customer, Invoice
from purchases.models import Supplier, PurchaseInvoice


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating various reports
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Get dashboard summary statistics
        """
        today = timezone.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Sales statistics
        total_sales = SaleOrder.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        this_month_sales = SaleOrder.objects.filter(
            status='delivered',
            order_date__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Purchase statistics
        total_purchases = PurchaseInvoice.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        this_month_purchases = PurchaseInvoice.objects.filter(
            invoice_date__gte=this_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Inventory statistics
        total_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=F('min_stock_level'),
            is_active=True
        ).count()
        
        total_inventory_value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock_quantity') * F('cost_price'))
        )['total'] or 0
        
        # Customer and supplier statistics
        total_customers = Customer.objects.filter(is_active=True).count()
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        
        # Recent activities
        recent_sales = SaleOrder.objects.all().order_by('-created_at')[:5]
        recent_purchases = PurchaseInvoice.objects.all().order_by('-created_at')[:5]
        
        return Response({
            'sales': {
                'total_sales': float(total_sales),
                'this_month_sales': float(this_month_sales),
                'recent_sales': [
                    {
                        'order_number': sale.order_number,
                        'customer': sale.customer.name,
                        'total_amount': float(sale.total_amount),
                        'status': sale.status
                    } for sale in recent_sales
                ]
            },
            'purchases': {
                'total_purchases': float(total_purchases),
                'this_month_purchases': float(this_month_purchases),
                'recent_purchases': [
                    {
                        'invoice_number': purchase.invoice_number,
                        'supplier': purchase.supplier.name,
                        'amount': float(purchase.amount),
                        'status': purchase.status
                    } for purchase in recent_purchases
                ]
            },
            'inventory': {
                'total_products': total_products,
                'low_stock_products': low_stock_products,
                'total_inventory_value': float(total_inventory_value)
            },
            'partners': {
                'total_customers': total_customers,
                'total_suppliers': total_suppliers
            }
        })

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        """
        Generate sales report
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = SaleOrder.objects.filter(status='delivered')
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Sales by date
        sales_by_date = queryset.values('order_date').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('order_date')
        
        # Top customers
        top_customers = queryset.values('customer__name').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        # Sales summary
        total_sales = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = queryset.count()
        avg_order_value = queryset.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        return Response({
            'summary': {
                'total_sales': float(total_sales),
                'total_orders': total_orders,
                'average_order_value': float(avg_order_value)
            },
            'sales_by_date': list(sales_by_date),
            'top_customers': list(top_customers)
        })

    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        """
        Generate inventory report
        """
        # Stock levels
        products = Product.objects.filter(is_active=True).annotate(
            stock_value=F('stock_quantity') * F('cost_price')
        ).order_by('-stock_value')
        
        # Categories summary
        categories_summary = Category.objects.annotate(
            product_count=Count('products'),
            total_stock=Sum('products__stock_quantity'),
            total_value=Sum(F('products__stock_quantity') * F('products__cost_price'))
        )
        
        # Low stock products
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=F('min_stock_level'),
            is_active=True
        )
        
        # Recent stock movements
        recent_movements = StockMovement.objects.all().order_by('-created_at')[:20]
        
        return Response({
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'stock_quantity': product.stock_quantity,
                    'stock_value': float(product.stock_value),
                    'category': product.category.name
                } for product in products
            ],
            'categories_summary': [
                {
                    'name': cat.name,
                    'product_count': cat.product_count,
                    'total_stock': cat.total_stock or 0,
                    'total_value': float(cat.total_value or 0)
                } for cat in categories_summary
            ],
            'low_stock_products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'stock_quantity': product.stock_quantity,
                    'min_stock_level': product.min_stock_level
                } for product in low_stock_products
            ],
            'recent_movements': [
                {
                    'product': movement.product.name,
                    'movement_type': movement.movement_type,
                    'quantity': movement.quantity,
                    'created_at': movement.created_at
                } for movement in recent_movements
            ]
        })

    @action(detail=False, methods=['get'])
    def financial_report(self, request):
        """
        Generate financial report
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Sales revenue
        sales_queryset = SaleOrder.objects.filter(status='delivered')
        if start_date:
            sales_queryset = sales_queryset.filter(order_date__gte=start_date)
        if end_date:
            sales_queryset = sales_queryset.filter(order_date__lte=end_date)
        
        total_revenue = sales_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Purchase costs
        purchase_queryset = PurchaseInvoice.objects.all()
        if start_date:
            purchase_queryset = purchase_queryset.filter(invoice_date__gte=start_date)
        if end_date:
            purchase_queryset = purchase_queryset.filter(invoice_date__lte=end_date)
        
        total_costs = purchase_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Inventory value
        inventory_value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock_quantity') * F('cost_price'))
        )['total'] or 0
        
        # Outstanding invoices
        outstanding_sales = Invoice.objects.filter(
            status__in=['pending', 'partial']
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        outstanding_purchases = PurchaseInvoice.objects.filter(
            status__in=['pending', 'partial']
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        # Profit calculation
        gross_profit = total_revenue - total_costs
        
        return Response({
            'revenue': {
                'total_revenue': float(total_revenue),
                'outstanding_receivables': float(outstanding_sales)
            },
            'costs': {
                'total_costs': float(total_costs),
                'outstanding_payables': float(outstanding_purchases)
            },
            'inventory': {
                'inventory_value': float(inventory_value)
            },
            'profitability': {
                'gross_profit': float(gross_profit),
                'gross_margin': float((gross_profit / total_revenue * 100) if total_revenue > 0 else 0)
            }
        })

    @action(detail=False, methods=['get'])
    def customer_report(self, request):
        """
        Generate customer report
        """
        # Top customers by sales
        top_customers = Customer.objects.filter(is_active=True).annotate(
            total_sales=Sum('orders__total_amount'),
            order_count=Count('orders')
        ).filter(total_sales__isnull=False).order_by('-total_sales')[:20]
        
        # Customer activity
        active_customers = Customer.objects.filter(
            orders__created_at__gte=timezone.now() - timedelta(days=30)
        ).distinct().count()
        
        total_customers = Customer.objects.filter(is_active=True).count()
        
        return Response({
            'summary': {
                'total_customers': total_customers,
                'active_customers': active_customers
            },
            'top_customers': [
                {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'total_sales': float(customer.total_sales or 0),
                    'order_count': customer.order_count
                } for customer in top_customers
            ]
        })

    @action(detail=False, methods=['get'])
    def supplier_report(self, request):
        """
        Generate supplier report
        """
        # Top suppliers by purchases
        top_suppliers = Supplier.objects.filter(is_active=True).annotate(
            total_purchases=Sum('invoices__amount'),
            invoice_count=Count('invoices')
        ).filter(total_purchases__isnull=False).order_by('-total_purchases')[:20]
        
        # Supplier activity
        active_suppliers = Supplier.objects.filter(
            invoices__created_at__gte=timezone.now() - timedelta(days=30)
        ).distinct().count()
        
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        
        return Response({
            'summary': {
                'total_suppliers': total_suppliers,
                'active_suppliers': active_suppliers
            },
                            'top_suppliers': [
                    {
                        'id': supplier.id,
                        'name': supplier.name,
                        'email': supplier.email,
                        'total_purchases': float(supplier.total_purchases or 0),
                        'invoice_count': supplier.invoice_count
                    } for supplier in top_suppliers
                ]
        })
