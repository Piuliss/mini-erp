from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from users.models import User
from inventory.models import Category, Product
from .models import Customer, SaleOrder, SaleOrderItem, Invoice


class CustomerModelTest(TestCase):
    """Tests para el modelo Customer"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            address="Test Address"
        )
    
    def test_customer_creation(self):
        """Test que se puede crear un cliente"""
        self.assertEqual(self.customer.name, "Test Customer")
        self.assertEqual(self.customer.email, "customer@example.com")
        self.assertEqual(self.customer.phone, "+1234567890")
        self.assertEqual(self.customer.address, "Test Address")
        self.assertTrue(self.customer.is_active)
        self.assertIsNotNone(self.customer.created_at)
        self.assertIsNotNone(self.customer.updated_at)
    
    def test_customer_str_representation(self):
        """Test la representación string del cliente"""
        self.assertEqual(str(self.customer), "Test Customer")


class SaleOrderModelTest(TestCase):
    """Tests para el modelo SaleOrder"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com"
        )
        self.sale_order = SaleOrder.objects.create(
            customer=self.customer,
            status="draft",
            order_date=timezone.now().date(),
            delivery_date=timezone.now().date() + timezone.timedelta(days=7),
            notes="Test order",
            created_by=self.user
        )
    
    def test_sale_order_creation(self):
        """Test que se puede crear una orden de venta"""
        self.assertEqual(self.sale_order.customer, self.customer)
        self.assertEqual(self.sale_order.status, "draft")
        self.assertEqual(self.sale_order.created_by, self.user)
        self.assertEqual(self.sale_order.notes, "Test order")
        self.assertEqual(float(self.sale_order.subtotal), 0.0)
        self.assertEqual(float(self.sale_order.tax_amount), 0.0)
        self.assertEqual(float(self.sale_order.total_amount), 0.0)
        self.assertIsNotNone(self.sale_order.created_at)
        self.assertIsNotNone(self.sale_order.updated_at)
    
    def test_sale_order_str_representation(self):
        """Test la representación string de la orden"""
        self.assertTrue(str(self.sale_order).startswith("SO-"))
    
    def test_sale_order_number_generation(self):
        """Test que se genera automáticamente el número de orden"""
        self.assertIsNotNone(self.sale_order.order_number)
        self.assertTrue(self.sale_order.order_number.startswith("SO-"))
    
    def test_sale_order_calculate_totals(self):
        """Test el cálculo de totales de la orden"""
        # Crear productos y items
        category = Category.objects.create(name="Test Category")
        product1 = Product.objects.create(
            name="Product 1",
            sku="PROD-001",
            category=category,
            price=100.00,
            cost_price=60.00,
            created_by=self.user
        )
        product2 = Product.objects.create(
            name="Product 2",
            sku="PROD-002",
            category=category,
            price=50.00,
            cost_price=30.00,
            created_by=self.user
        )
        
        # Crear items de la orden
        SaleOrderItem.objects.create(
            order=self.sale_order,
            product=product1,
            quantity=2,
            unit_price=100.00
        )
        SaleOrderItem.objects.create(
            order=self.sale_order,
            product=product2,
            quantity=1,
            unit_price=50.00
        )
        
        # Calcular totales
        self.sale_order.calculate_totals()
        
        # Verificar cálculos
        self.assertEqual(float(self.sale_order.subtotal), 250.00)  # 2*100 + 1*50
        self.assertEqual(float(self.sale_order.tax_amount), 25.00)  # 10% de 250
        self.assertEqual(float(self.sale_order.total_amount), 275.00)  # 250 + 25


class SaleOrderItemModelTest(TestCase):
    """Tests para el modelo SaleOrderItem"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com"
        )
        self.sale_order = SaleOrder.objects.create(
            customer=self.customer,
            order_date=timezone.now().date(),
            created_by=self.user
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-001",
            category=self.category,
            price=100.00,
            cost_price=60.00,
            created_by=self.user
        )
    
    def test_sale_order_item_creation(self):
        """Test que se puede crear un item de orden"""
        item = SaleOrderItem.objects.create(
            order=self.sale_order,
            product=self.product,
            quantity=3,
            unit_price=100.00
        )
        
        self.assertEqual(item.order, self.sale_order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(float(item.unit_price), 100.00)
        self.assertEqual(float(item.total_price), 300.00)  # 3 * 100
        self.assertIsNotNone(item.created_at)
    
    def test_sale_order_item_str_representation(self):
        """Test la representación string del item"""
        item = SaleOrderItem.objects.create(
            order=self.sale_order,
            product=self.product,
            quantity=2,
            unit_price=100.00
        )
        expected = "Test Product - 2"
        self.assertEqual(str(item), expected)
    
    def test_sale_order_item_total_price_calculation(self):
        """Test el cálculo automático del precio total"""
        item = SaleOrderItem.objects.create(
            order=self.sale_order,
            product=self.product,
            quantity=5,
            unit_price=75.50
        )
        
        expected_total = 5 * 75.50
        self.assertEqual(float(item.total_price), expected_total)


class InvoiceModelTest(TestCase):
    """Tests para el modelo Invoice"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="customer@example.com"
        )
        self.sale_order = SaleOrder.objects.create(
            customer=self.customer,
            order_date=timezone.now().date(),
            total_amount=1000.00,
            created_by=self.user
        )
        self.invoice = Invoice.objects.create(
            sale_order=self.sale_order,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            amount=1000.00
        )
    
    def test_invoice_creation(self):
        """Test que se puede crear una factura"""
        self.assertEqual(self.invoice.sale_order, self.sale_order)
        self.assertEqual(float(self.invoice.amount), 1000.00)
        self.assertEqual(float(self.invoice.paid_amount), 0.0)
        self.assertEqual(self.invoice.status, "pending")
        self.assertIsNotNone(self.invoice.created_at)
        self.assertIsNotNone(self.invoice.updated_at)
    
    def test_invoice_str_representation(self):
        """Test la representación string de la factura"""
        self.assertTrue(str(self.invoice).startswith("INV-"))
    
    def test_invoice_number_generation(self):
        """Test que se genera automáticamente el número de factura"""
        self.assertIsNotNone(self.invoice.invoice_number)
        self.assertTrue(self.invoice.invoice_number.startswith("INV-"))
    
    def test_invoice_balance_property(self):
        """Test la propiedad balance de la factura"""
        self.assertEqual(float(self.invoice.balance), 1000.00)  # amount - paid_amount
        
        # Actualizar paid_amount
        self.invoice.paid_amount = 300.00
        self.invoice.save()
        self.assertEqual(float(self.invoice.balance), 700.00)
    
    def test_invoice_status_updates(self):
        """Test las actualizaciones de estado de la factura"""
        # Estado inicial
        self.assertEqual(self.invoice.status, "pending")
        
        # Pago parcial
        self.invoice.paid_amount = 500.00
        self.invoice.update_status()
        self.assertEqual(self.invoice.status, "partial")
        
        # Pago completo
        self.invoice.paid_amount = 1000.00
        self.invoice.update_status()
        self.assertEqual(self.invoice.status, "paid")
