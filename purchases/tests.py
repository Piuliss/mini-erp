from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import Supplier, PurchaseInvoice, PurchaseInvoiceItem
from inventory.models import Category, Product
from users.models import User, Role


class SupplierModelTest(TestCase):
    """Tests for Supplier model"""
    
    def setUp(self):
        self.supplier_data = {
            'name': 'Test Supplier',
            'email': 'test@supplier.com',
            'phone': '+1234567890',
            'address': 'Test Address',
            'contact_person': 'John Doe'
        }
    
    def test_supplier_creation(self):
        """Test supplier creation"""
        supplier = Supplier.objects.create(**self.supplier_data)
        self.assertEqual(supplier.name, self.supplier_data['name'])
        self.assertEqual(supplier.email, self.supplier_data['email'])
        self.assertTrue(supplier.is_active)
    
    def test_supplier_str(self):
        """Test supplier string representation"""
        supplier = Supplier.objects.create(**self.supplier_data)
        self.assertEqual(str(supplier), self.supplier_data['name'])
    
    def test_supplier_unique_name(self):
        """Test supplier name uniqueness"""
        Supplier.objects.create(**self.supplier_data)
        # Should be able to create another supplier with different name
        supplier2_data = self.supplier_data.copy()
        supplier2_data['name'] = 'Another Supplier'
        supplier2 = Supplier.objects.create(**supplier2_data)
        self.assertNotEqual(supplier2.name, self.supplier_data['name'])


class PurchaseInvoiceModelTest(TestCase):
    """Tests for PurchaseInvoice model"""
    
    def setUp(self):
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            email='test@supplier.com',
            phone='+1234567890',
            address='Test Address'
        )
        
        # Create user first
        self.role = Role.objects.create(name='Test Role')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='testpass123',
            role=self.role
        )
        
        # Create product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            category=self.category,
            price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            stock_quantity=10,
            created_by=self.user
        )
        
        self.invoice_data = {
            'supplier': self.supplier,
            'invoice_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'amount': Decimal('1000.00'),
            'notes': 'Test invoice'
        }
    
    def test_invoice_creation(self):
        """Test invoice creation"""
        invoice = PurchaseInvoice.objects.create(**self.invoice_data)
        self.assertEqual(invoice.supplier, self.supplier)
        self.assertEqual(invoice.amount, self.invoice_data['amount'])
        self.assertEqual(invoice.status, 'pending')
        self.assertTrue(invoice.invoice_number.startswith('PINV-'))
    
    def test_invoice_str(self):
        """Test invoice string representation"""
        invoice = PurchaseInvoice.objects.create(**self.invoice_data)
        self.assertEqual(str(invoice), f"PINV-{invoice.invoice_number.split('-')[1]}")
    
    def test_invoice_balance(self):
        """Test invoice balance calculation"""
        invoice = PurchaseInvoice.objects.create(**self.invoice_data)
        self.assertEqual(invoice.balance, Decimal('1000.00'))
        
        invoice.paid_amount = Decimal('500.00')
        invoice.save()
        self.assertEqual(invoice.balance, Decimal('500.00'))
    
    def test_invoice_status_update(self):
        """Test invoice status updates"""
        invoice = PurchaseInvoice.objects.create(**self.invoice_data)
        
        # Test pending status
        self.assertEqual(invoice.status, 'pending')
        
        # Test partial payment
        invoice.paid_amount = Decimal('500.00')
        invoice.update_status()
        self.assertEqual(invoice.status, 'partial')
        
        # Test full payment
        invoice.paid_amount = Decimal('1000.00')
        invoice.update_status()
        self.assertEqual(invoice.status, 'paid')


class PurchaseInvoiceItemModelTest(TestCase):
    """Tests for PurchaseInvoiceItem model"""
    
    def setUp(self):
        # Create user first
        self.role = Role.objects.create(name='Test Role')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            password='testpass123',
            role=self.role
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            email='test@supplier.com',
            phone='+1234567890',
            address='Test Address'
        )
        
        # Create product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            category=self.category,
            price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            stock_quantity=10,
            created_by=self.user
        )
        
        # Create invoice
        self.invoice = PurchaseInvoice.objects.create(
            supplier=self.supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=Decimal('0.00')
        )
        
        self.item_data = {
            'invoice': self.invoice,
            'product': self.product,
            'quantity': 5,
            'unit_price': Decimal('50.00')
        }
    
    def test_item_creation(self):
        """Test invoice item creation"""
        item = PurchaseInvoiceItem.objects.create(**self.item_data)
        self.assertEqual(item.invoice, self.invoice)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.total_price, Decimal('250.00'))
    
    def test_item_str(self):
        """Test invoice item string representation"""
        item = PurchaseInvoiceItem.objects.create(**self.item_data)
        self.assertEqual(str(item), f"{self.product.name} - 5")
    
    def test_item_stock_update(self):
        """Test that creating an item updates product stock"""
        initial_stock = self.product.stock_quantity
        item = PurchaseInvoiceItem.objects.create(**self.item_data)
        
        # Refresh product from database
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock + 5)
    
    def test_item_total_price_calculation(self):
        """Test item total price calculation"""
        item = PurchaseInvoiceItem.objects.create(**self.item_data)
        expected_total = Decimal('50.00') * 5
        self.assertEqual(item.total_price, expected_total)
    
    def test_invoice_amount_update(self):
        """Test that creating an item updates invoice amount"""
        item = PurchaseInvoiceItem.objects.create(**self.item_data)
        
        # Refresh invoice from database
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount, Decimal('250.00'))
