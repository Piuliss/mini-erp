from rest_framework import serializers
from .models import Customer, SaleOrder, SaleOrderItem, Invoice


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model
    """
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'is_active',
            'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_orders_count(self, obj):
        return obj.orders.count()


class SaleOrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for SaleOrderItem model
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')

    class Meta:
        model = SaleOrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class SaleOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for SaleOrder model
    """
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    items = SaleOrderItemSerializer(many=True, read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = SaleOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_id', 'status', 'status_display',
            'order_date', 'delivery_date', 'subtotal', 'tax_amount', 'total_amount',
            'notes', 'items', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax_amount', 'total_amount',
            'created_at', 'updated_at', 'created_by_name'
        ]


class SaleOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating sale orders with items
    """
    customer_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = SaleOrder
        fields = [
            'customer_id', 'order_date', 'delivery_date', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer_id = validated_data.pop('customer_id')
        
        # Create the sale order
        sale_order = SaleOrder.objects.create(
            customer_id=customer_id,
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            SaleOrderItem.objects.create(
                order=sale_order,
                **item_data
            )
        
        return sale_order


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model
    """
    sale_order_number = serializers.ReadOnlyField(source='sale_order.order_number')
    customer_name = serializers.ReadOnlyField(source='sale_order.customer.name')
    balance = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'sale_order', 'sale_order_number',
            'customer_name', 'invoice_date', 'due_date', 'amount',
            'paid_amount', 'balance', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating invoices
    """
    sale_order_id = serializers.IntegerField()

    class Meta:
        model = Invoice
        fields = ['sale_order_id', 'invoice_date', 'due_date']

    def create(self, validated_data):
        sale_order_id = validated_data.pop('sale_order_id')
        sale_order = SaleOrder.objects.get(id=sale_order_id)
        
        return Invoice.objects.create(
            sale_order=sale_order,
            amount=sale_order.total_amount,
            **validated_data
        )
