from django.contrib import admin
from .models import Supplier, PurchaseInvoice, PurchaseInvoiceItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'contact_person', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'contact_person']
    ordering = ['name']


class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'total_price']


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'due_date', 'amount', 'paid_amount', 'status', 'created_at']
    list_filter = ['status', 'invoice_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'supplier__name']
    ordering = ['-created_at']
    inlines = [PurchaseInvoiceItemInline]
    readonly_fields = ['invoice_number', 'amount', 'created_at', 'updated_at']
