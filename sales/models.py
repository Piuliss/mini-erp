from django.db import models
from decimal import Decimal
from users.models import User
from inventory.models import Product


class Customer(models.Model):
    """
    Customer model
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return self.name


class SaleOrder(models.Model):
    """
    Sale order model
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sale_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"SO-{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            last_order = SaleOrder.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[1])
                self.order_number = f"SO-{last_number + 1:06d}"
            else:
                self.order_number = "SO-000001"
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate order totals"""
        subtotal = sum(item.total_price for item in self.items.all())
        self.subtotal = subtotal
        self.tax_amount = subtotal * Decimal('0.10')  # 10% tax
        self.total_amount = self.subtotal + self.tax_amount
        self.save()


class SaleOrderItem(models.Model):
    """
    Sale order item model
    """
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sale_order_items'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update order totals
        self.order.calculate_totals()


class Invoice(models.Model):
    """
    Invoice model
    """
    invoice_number = models.CharField(max_length=20, unique=True)
    sale_order = models.OneToOneField(SaleOrder, on_delete=models.CASCADE, related_name='invoice')
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'

    def __str__(self):
        return f"INV-{self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[1])
                self.invoice_number = f"INV-{last_number + 1:06d}"
            else:
                self.invoice_number = "INV-000001"
        super().save(*args, **kwargs)

    @property
    def balance(self):
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
