from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseInvoice


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'contact_person', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'contact_person']
    ordering = ['-created_at']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'status', 'total_amount', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'supplier__name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'subtotal', 'tax_amount', 'total_amount']
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'purchase_order', 'amount', 'paid_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'purchase_order__order_number']
    ordering = ['-created_at']
    readonly_fields = ['invoice_number', 'balance']
