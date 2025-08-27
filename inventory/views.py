from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, F
from .models import Category, Product, StockMovement
from .serializers import (
    CategorySerializer, ProductSerializer, StockMovementSerializer,
    ProductStockSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all().order_by('name')

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in a category
        """
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        
        # Filter by category
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status', None)
        if stock_status:
            if stock_status == 'low':
                queryset = queryset.filter(stock_quantity__lte=F('min_stock_level'))
            elif stock_status == 'high':
                queryset = queryset.filter(stock_quantity__gte=F('max_stock_level'))
            elif stock_status == 'normal':
                queryset = queryset.filter(
                    stock_quantity__gt=F('min_stock_level'),
                    stock_quantity__lt=F('max_stock_level')
                )
        
        # Search by name or SKU
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """
        Adjust product stock quantity
        """
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('movement_type', 'adjustment')
        reference = request.data.get('reference', '')
        notes = request.data.get('notes', '')

        if not quantity:
            return Response(
                {'error': 'Quantity is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create stock movement
        StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=abs(quantity),
            reference=reference,
            notes=notes,
            created_by=request.user
        )

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get products with low stock
        """
        products = Product.objects.filter(
            stock_quantity__lte=F('min_stock_level'),
            is_active=True
        )
        serializer = ProductStockSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_summary(self, request):
        """
        Get stock summary statistics
        """
        total_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=F('min_stock_level'),
            is_active=True
        ).count()
        out_of_stock = Product.objects.filter(
            stock_quantity=0,
            is_active=True
        ).count()
        total_value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock_quantity') * F('cost_price'))
        )['total'] or 0

        return Response({
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock': out_of_stock,
            'total_inventory_value': float(total_value)
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock movements
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StockMovement.objects.all().order_by('-created_at')
        
        # Filter by product
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by movement type
        movement_type = self.request.query_params.get('movement_type', None)
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def recent_movements(self, request):
        """
        Get recent stock movements
        """
        movements = StockMovement.objects.all().order_by('-created_at')[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)
