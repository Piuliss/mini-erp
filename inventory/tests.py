from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User
from .models import Category, Product, StockMovement


class CategoryModelTest(TestCase):
    """Tests para el modelo Category"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description"
        )
    
    def test_category_creation(self):
        """Test que se puede crear una categoría"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.description, "Test category description")
        self.assertIsNotNone(self.category.created_at)
        self.assertIsNotNone(self.category.updated_at)
    
    def test_category_str_representation(self):
        """Test la representación string de la categoría"""
        self.assertEqual(str(self.category), "Test Category")
    
    def test_category_unique_name(self):
        """Test que el nombre de la categoría debe ser único"""
        with self.assertRaises(Exception):  # IntegrityError
            Category.objects.create(name="Test Category", description="Another description")


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            sku="TEST-001",
            category=self.category,
            price=100.00,
            cost_price=60.00,
            stock_quantity=50,
            min_stock_level=10,
            max_stock_level=200,
            created_by=self.user
        )
    
    def test_product_creation(self):
        """Test que se puede crear un producto"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "Test product description")
        self.assertEqual(self.product.sku, "TEST-001")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(float(self.product.price), 100.00)
        self.assertEqual(float(self.product.cost_price), 60.00)
        self.assertEqual(self.product.stock_quantity, 50)
        self.assertEqual(self.product.min_stock_level, 10)
        self.assertEqual(self.product.max_stock_level, 200)
        self.assertEqual(self.product.created_by, self.user)
        self.assertTrue(self.product.is_active)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)
    
    def test_product_str_representation(self):
        """Test la representación string del producto"""
        expected = "Test Product (TEST-001)"
        self.assertEqual(str(self.product), expected)
    
    def test_product_sku_unique(self):
        """Test que el SKU debe ser único"""
        with self.assertRaises(Exception):  # IntegrityError
            Product.objects.create(
                name="Another Product",
                sku="TEST-001",
                category=self.category,
                price=50.00,
                cost_price=30.00,
                created_by=self.user
            )
    
    def test_product_stock_status_normal(self):
        """Test stock_status cuando el stock está normal"""
        self.assertEqual(self.product.stock_status, "normal")
    
    def test_product_stock_status_low(self):
        """Test stock_status cuando el stock está bajo"""
        self.product.stock_quantity = 5  # Menos que min_stock_level
        self.product.save()
        self.assertEqual(self.product.stock_status, "low")
    
    def test_product_stock_status_high(self):
        """Test stock_status cuando el stock está alto"""
        self.product.stock_quantity = 250  # Más que max_stock_level
        self.product.save()
        self.assertEqual(self.product.stock_status, "high")


class StockMovementModelTest(TestCase):
    """Tests para el modelo StockMovement"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-001",
            category=self.category,
            price=100.00,
            cost_price=60.00,
            stock_quantity=50,
            created_by=self.user
        )
    
    def test_stock_movement_creation_in(self):
        """Test crear movimiento de entrada de stock"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type="in",
            quantity=10,
            reference="PO-001",
            notes="Test stock in",
            created_by=self.user
        )
        
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.movement_type, "in")
        self.assertEqual(movement.quantity, 10)
        self.assertEqual(movement.previous_quantity, 50)
        self.assertEqual(movement.new_quantity, 60)
        self.assertEqual(movement.reference, "PO-001")
        self.assertEqual(movement.notes, "Test stock in")
        self.assertEqual(movement.created_by, self.user)
        
        # Verificar que el stock del producto se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 60)
    
    def test_stock_movement_creation_out(self):
        """Test crear movimiento de salida de stock"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type="out",
            quantity=5,
            reference="SO-001",
            notes="Test stock out",
            created_by=self.user
        )
        
        self.assertEqual(movement.movement_type, "out")
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.previous_quantity, 50)
        self.assertEqual(movement.new_quantity, 45)
        
        # Verificar que el stock del producto se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 45)
    
    def test_stock_movement_creation_adjustment(self):
        """Test crear movimiento de ajuste de stock"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type="adjustment",
            quantity=20,
            reference="ADJ-001",
            notes="Test adjustment",
            created_by=self.user
        )
        
        self.assertEqual(movement.movement_type, "adjustment")
        self.assertEqual(movement.quantity, 20)
        self.assertEqual(movement.previous_quantity, 50)
        self.assertEqual(movement.new_quantity, 30)
        
        # Verificar que el stock del producto se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 30)
    
    def test_stock_movement_creation_return(self):
        """Test crear movimiento de retorno de stock"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type="return",
            quantity=3,
            reference="RET-001",
            notes="Test return",
            created_by=self.user
        )
        
        self.assertEqual(movement.movement_type, "return")
        self.assertEqual(movement.quantity, 3)
        self.assertEqual(movement.previous_quantity, 50)
        self.assertEqual(movement.new_quantity, 53)
        
        # Verificar que el stock del producto se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 53)
    
    def test_stock_movement_str_representation(self):
        """Test la representación string del movimiento de stock"""
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type="in",
            quantity=10,
            created_by=self.user
        )
        expected = "Test Product - in (10)"
        self.assertEqual(str(movement), expected)
    
    def test_stock_movement_prevents_negative_stock(self):
        """Test que no se puede sacar más stock del disponible"""
        # Intentar sacar más stock del disponible
        with self.assertRaises(ValueError):
            StockMovement.objects.create(
                product=self.product,
                movement_type="out",
                quantity=100,  # Más que el stock disponible (50)
                created_by=self.user
            )
