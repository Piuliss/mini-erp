from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from users.models import User
from inventory.models import Category, Product
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseInvoice


class SupplierModelTest(TestCase):
    """Tests para el modelo Supplier"""
    
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com",
            phone="+1234567890",
            address="Test Address",
            contact_person="John Doe"
        )
    
    def test_supplier_creation(self):
        """Test que se puede crear un proveedor"""
        self.assertEqual(self.supplier.name, "Test Supplier")
        self.assertEqual(self.supplier.email, "supplier@example.com")
        self.assertEqual(self.supplier.phone, "+1234567890")
        self.assertEqual(self.supplier.address, "Test Address")
        self.assertEqual(self.supplier.contact_person, "John Doe")
        self.assertTrue(self.supplier.is_active)
        self.assertIsNotNone(self.supplier.created_at)
        self.assertIsNotNone(self.supplier.updated_at)
    
    def test_supplier_str_representation(self):
        """Test la representación string del proveedor"""
        self.assertEqual(str(self.supplier), "Test Supplier")


class PurchaseOrderModelTest(TestCase):
    """Tests para el modelo PurchaseOrder"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com"
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            status="draft",
            order_date=timezone.now().date(),
            expected_delivery=timezone.now().date() + timezone.timedelta(days=14),
            notes="Test purchase order",
            created_by=self.user
        )
    
    def test_purchase_order_creation(self):
        """Test que se puede crear una orden de compra"""
        self.assertEqual(self.purchase_order.supplier, self.supplier)
        self.assertEqual(self.purchase_order.status, "draft")
        self.assertEqual(self.purchase_order.created_by, self.user)
        self.assertEqual(self.purchase_order.notes, "Test purchase order")
        self.assertEqual(float(self.purchase_order.subtotal), 0.0)
        self.assertEqual(float(self.purchase_order.tax_amount), 0.0)
        self.assertEqual(float(self.purchase_order.total_amount), 0.0)
        self.assertIsNotNone(self.purchase_order.created_at)
        self.assertIsNotNone(self.purchase_order.updated_at)
    
    def test_purchase_order_str_representation(self):
        """Test la representación string de la orden"""
        self.assertTrue(str(self.purchase_order).startswith("PO-"))
    
    def test_purchase_order_number_generation(self):
        """Test que se genera automáticamente el número de orden"""
        self.assertIsNotNone(self.purchase_order.order_number)
        self.assertTrue(self.purchase_order.order_number.startswith("PO-"))
    
    def test_purchase_order_calculate_totals(self):
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
        PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=product1,
            quantity=3,
            unit_price=60.00
        )
        PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=product2,
            quantity=2,
            unit_price=30.00
        )
        
        # Calcular totales
        self.purchase_order.calculate_totals()
        
        # Verificar cálculos
        self.assertEqual(float(self.purchase_order.subtotal), 240.00)  # 3*60 + 2*30
        self.assertEqual(float(self.purchase_order.tax_amount), 24.00)  # 10% de 240
        self.assertEqual(float(self.purchase_order.total_amount), 264.00)  # 240 + 24


class PurchaseOrderItemModelTest(TestCase):
    """Tests para el modelo PurchaseOrderItem"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com"
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_date=timezone.now().date(),
            expected_delivery=timezone.now().date() + timezone.timedelta(days=14),
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
    
    def test_purchase_order_item_creation(self):
        """Test que se puede crear un item de orden de compra"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=self.product,
            quantity=5,
            unit_price=60.00
        )
        
        self.assertEqual(item.order, self.purchase_order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(float(item.unit_price), 60.00)
        self.assertEqual(float(item.total_price), 300.00)  # 5 * 60
        self.assertEqual(item.received_quantity, 0)
        self.assertIsNotNone(item.created_at)
    
    def test_purchase_order_item_str_representation(self):
        """Test la representación string del item"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=self.product,
            quantity=4,
            unit_price=60.00
        )
        expected = "Test Product - 4"
        self.assertEqual(str(item), expected)
    
    def test_purchase_order_item_total_price_calculation(self):
        """Test el cálculo automático del precio total"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=self.product,
            quantity=6,
            unit_price=45.50
        )
        
        expected_total = 6 * 45.50
        self.assertEqual(float(item.total_price), expected_total)
    
    def test_purchase_order_item_remaining_quantity(self):
        """Test la propiedad remaining_quantity"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product=self.product,
            quantity=10,
            unit_price=60.00
        )
        
        # Sin recibir nada
        self.assertEqual(item.remaining_quantity, 10)
        
        # Recibir parcialmente
        item.received_quantity = 3
        item.save()
        self.assertEqual(item.remaining_quantity, 7)
        
        # Recibir completamente
        item.received_quantity = 10
        item.save()
        self.assertEqual(item.remaining_quantity, 0)


class PurchaseInvoiceModelTest(TestCase):
    """Tests para el modelo PurchaseInvoice"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="supplier@example.com"
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_date=timezone.now().date(),
            expected_delivery=timezone.now().date() + timezone.timedelta(days=14),
            total_amount=800.00,
            created_by=self.user
        )
        self.invoice = PurchaseInvoice.objects.create(
            purchase_order=self.purchase_order,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            amount=800.00
        )
    
    def test_purchase_invoice_creation(self):
        """Test que se puede crear una factura de compra"""
        self.assertEqual(self.invoice.purchase_order, self.purchase_order)
        self.assertEqual(float(self.invoice.amount), 800.00)
        self.assertEqual(float(self.invoice.paid_amount), 0.0)
        self.assertEqual(self.invoice.status, "pending")
        self.assertIsNotNone(self.invoice.created_at)
        self.assertIsNotNone(self.invoice.updated_at)
    
    def test_purchase_invoice_str_representation(self):
        """Test la representación string de la factura"""
        self.assertTrue(str(self.invoice).startswith("PINV-"))
    
    def test_purchase_invoice_number_generation(self):
        """Test que se genera automáticamente el número de factura"""
        self.assertIsNotNone(self.invoice.invoice_number)
        self.assertTrue(self.invoice.invoice_number.startswith("PINV-"))
    
    def test_purchase_invoice_balance_property(self):
        """Test la propiedad balance de la factura"""
        self.assertEqual(float(self.invoice.balance), 800.00)  # amount - paid_amount
        
        # Actualizar paid_amount
        self.invoice.paid_amount = 200.00
        self.invoice.save()
        self.assertEqual(float(self.invoice.balance), 600.00)
    
    def test_purchase_invoice_status_updates(self):
        """Test las actualizaciones de estado de la factura"""
        # Estado inicial
        self.assertEqual(self.invoice.status, "pending")
        
        # Pago parcial
        self.invoice.paid_amount = 400.00
        self.invoice.update_status()
        self.assertEqual(self.invoice.status, "partial")
        
        # Pago completo
        self.invoice.paid_amount = 800.00
        self.invoice.update_status()
        self.assertEqual(self.invoice.status, "paid")
