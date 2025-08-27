from django.contrib import admin
from .models import Customer, SaleOrder, SaleOrderItem, Invoice


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email']
    ordering = ['-created_at']


class SaleOrderItemInline(admin.TabularInline):
    model = SaleOrderItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'subtotal', 'tax_amount', 'total_amount']
    inlines = [SaleOrderItemInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'sale_order', 'amount', 'paid_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'sale_order__order_number']
    ordering = ['-created_at']
    readonly_fields = ['invoice_number', 'balance']
