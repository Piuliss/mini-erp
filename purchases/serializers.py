from django.db import transaction
from rest_framework import serializers
from .models import Supplier, PurchaseInvoice, PurchaseInvoiceItem


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for Supplier model
    """
    invoices_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'contact_person',
            'is_active', 'invoices_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_invoices_count(self, obj):
        return obj.invoices.count()


class PurchaseInvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseInvoiceItem model
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')

    class Meta:
        model = PurchaseInvoiceItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class PurchaseInvoiceItemCreateSerializer(serializers.Serializer):
    """
    Typed payload for purchase invoice line items.
    Coerces unit_price from string/number to Decimal (avoids qty * str bug).
    """
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseInvoice model
    """
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField()
    items = PurchaseInvoiceItemSerializer(many=True, read_only=True)
    balance = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'invoice_number', 'supplier', 'supplier_id', 'status', 'status_display',
            'invoice_date', 'due_date', 'amount', 'paid_amount', 'balance',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'amount', 'created_at', 'updated_at'
        ]


class PurchaseInvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating purchase invoices with items
    """
    supplier_id = serializers.IntegerField()
    items = PurchaseInvoiceItemCreateSerializer(many=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'supplier_id', 'invoice_date', 'due_date', 'notes', 'items'
        ]
        read_only_fields = ['id']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        supplier_id = validated_data.pop('supplier_id')

        with transaction.atomic():
            purchase_invoice = PurchaseInvoice.objects.create(
                supplier_id=supplier_id,
                **validated_data
            )

            for item_data in items_data:
                PurchaseInvoiceItem.objects.create(
                    invoice=purchase_invoice,
                    product_id=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                )

            purchase_invoice.refresh_from_db()

        return purchase_invoice

    def to_representation(self, instance):
        return PurchaseInvoiceSerializer(instance, context=self.context).data
