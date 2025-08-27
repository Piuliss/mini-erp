from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Role, User


class RoleModelTest(TestCase):
    """Tests para el modelo Role"""
    
    def setUp(self):
        self.role = Role.objects.create(
            name="Test Role",
            description="Test role description"
        )
    
    def test_role_creation(self):
        """Test que se puede crear un rol"""
        self.assertEqual(self.role.name, "Test Role")
        self.assertEqual(self.role.description, "Test role description")
        self.assertIsNotNone(self.role.created_at)
        self.assertIsNotNone(self.role.updated_at)
    
    def test_role_str_representation(self):
        """Test la representación string del rol"""
        self.assertEqual(str(self.role), "Test Role")
    
    def test_role_unique_name(self):
        """Test que el nombre del rol debe ser único"""
        with self.assertRaises(Exception):  # IntegrityError o ValidationError
            Role.objects.create(name="Test Role", description="Another description")


class UserModelTest(TestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        self.role = Role.objects.create(name="Test Role")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            address="Test Address",
            role=self.role
        )
    
    def test_user_creation(self):
        """Test que se puede crear un usuario"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertEqual(self.user.phone, "+1234567890")
        self.assertEqual(self.user.address, "Test Address")
        self.assertEqual(self.user.role, self.role)
        self.assertTrue(self.user.is_active)
        self.assertIsNotNone(self.user.created_at)
        self.assertIsNotNone(self.user.updated_at)
    
    def test_user_str_representation(self):
        """Test la representación string del usuario"""
        self.assertEqual(str(self.user), "test@example.com")
    
    def test_user_full_name_property(self):
        """Test la propiedad full_name"""
        self.assertEqual(self.user.full_name, "Test User")
    
    def test_user_full_name_without_last_name(self):
        """Test full_name cuando no hay apellido"""
        user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test"
        )
        self.assertEqual(user.full_name, "Test")
    
    def test_user_email_unique(self):
        """Test que el email debe ser único"""
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(
                username="testuser3",
                email="test@example.com",
                password="testpass123"
            )
    
    def test_user_username_unique(self):
        """Test que el username debe ser único"""
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(
                username="testuser",
                email="test3@example.com",
                password="testpass123"
            )
    
    def test_user_without_role(self):
        """Test crear usuario sin rol"""
        user = User.objects.create_user(
            username="testuser4",
            email="test4@example.com",
            password="testpass123"
        )
        self.assertIsNone(user.role)
    
    def test_user_password_hashing(self):
        """Test que la contraseña se hashea correctamente"""
        self.assertNotEqual(self.user.password, "testpass123")
        self.assertTrue(self.user.check_password("testpass123"))
    
    def test_create_superuser(self):
        """Test crear superusuario"""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
