from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseInvoice


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for Supplier model
    """
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'contact_person',
            'is_active', 'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_orders_count(self, obj):
        return obj.orders.count()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseOrderItem model
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')
    remaining_quantity = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'received_quantity', 'remaining_quantity',
            'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseOrder model
    """
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_id', 'status', 'status_display',
            'order_date', 'expected_delivery', 'delivery_date', 'subtotal', 'tax_amount',
            'total_amount', 'notes', 'items', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax_amount', 'total_amount',
            'created_at', 'updated_at', 'created_by_name'
        ]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating purchase orders with items
    """
    supplier_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier_id', 'order_date', 'expected_delivery', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        supplier_id = validated_data.pop('supplier_id')
        
        # Create the purchase order
        purchase_order = PurchaseOrder.objects.create(
            supplier_id=supplier_id,
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                order=purchase_order,
                **item_data
            )
        
        return purchase_order


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseInvoice model
    """
    purchase_order_number = serializers.ReadOnlyField(source='purchase_order.order_number')
    supplier_name = serializers.ReadOnlyField(source='purchase_order.supplier.name')
    balance = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'invoice_number', 'purchase_order', 'purchase_order_number',
            'supplier_name', 'invoice_date', 'due_date', 'amount',
            'paid_amount', 'balance', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at'
        ]


class PurchaseInvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating purchase invoices
    """
    purchase_order_id = serializers.IntegerField()

    class Meta:
        model = PurchaseInvoice
        fields = ['purchase_order_id', 'invoice_date', 'due_date']

    def create(self, validated_data):
        purchase_order_id = validated_data.pop('purchase_order_id')
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        
        return PurchaseInvoice.objects.create(
            purchase_order=purchase_order,
            amount=purchase_order.total_amount,
            **validated_data
        )
