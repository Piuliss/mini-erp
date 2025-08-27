from django.db import models
from users.models import User


class Category(models.Model):
    """
    Product category model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=0)
    max_stock_level = models.IntegerField(default=1000)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def stock_status(self):
        if self.stock_quantity <= self.min_stock_level:
            return 'low'
        elif self.stock_quantity >= self.max_stock_level:
            return 'high'
        return 'normal'


class StockMovement(models.Model):
    """
    Stock movement model for tracking inventory changes
    """
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Stock Adjustment'),
        ('return', 'Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)  # Purchase order, sale order, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.previous_quantity = self.product.stock_quantity
            if self.movement_type in ['in', 'return']:
                self.new_quantity = self.previous_quantity + self.quantity
            else:
                # Check if we have enough stock
                if self.previous_quantity < self.quantity:
                    raise ValueError(f"Insufficient stock. Available: {self.previous_quantity}, Requested: {self.quantity}")
                self.new_quantity = self.previous_quantity - self.quantity
            
            # Update product stock
            self.product.stock_quantity = self.new_quantity
            self.product.save()
        
        super().save(*args, **kwargs)
