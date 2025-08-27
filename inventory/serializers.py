from rest_framework import serializers
from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    stock_status = serializers.ReadOnlyField()
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'category', 'category_id',
            'price', 'cost_price', 'stock_quantity', 'min_stock_level',
            'max_stock_level', 'is_active', 'stock_status', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name']


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer for StockMovement model
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')
    movement_type_display = serializers.ReadOnlyField(source='get_movement_type_display')

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'movement_type_display',
            'quantity', 'previous_quantity', 'new_quantity', 'reference', 'notes',
            'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'previous_quantity', 'new_quantity', 'created_at', 'created_by_name'
        ]


class ProductStockSerializer(serializers.ModelSerializer):
    """
    Serializer for product stock information
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    stock_status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category_name', 'stock_quantity',
            'min_stock_level', 'max_stock_level', 'stock_status'
        ]
