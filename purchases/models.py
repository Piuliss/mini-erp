from django.db import models
from decimal import Decimal
from inventory.models import Product


class Supplier(models.Model):
    """
    Supplier model
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    contact_person = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return self.name


class PurchaseInvoice(models.Model):
    """
    Purchase invoice model
    """
    invoice_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_invoices'

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            last_invoice = PurchaseInvoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[1])
                self.invoice_number = f"PINV-{last_number + 1:06d}"
            else:
                self.invoice_number = "PINV-000001"
        super().save(*args, **kwargs)

    @property
    def balance(self):
        if self.amount is None:
            return Decimal('0.00') - self.paid_amount
        return self.amount - self.paid_amount
    
    def update_status(self):
        """Update invoice status based on paid amount"""
        if self.paid_amount >= self.amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save()


class PurchaseInvoiceItem(models.Model):
    """
    Purchase invoice item model
    """
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchase_invoice_items'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update invoice amount
        self.invoice.amount = sum(item.total_price for item in self.invoice.items.all())
        self.invoice.save()
        
        # Update product stock only on creation
        if is_new:
            self.product.stock_quantity += self.quantity
            self.product.save()
