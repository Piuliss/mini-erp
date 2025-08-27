"""
Tests End-to-End para el módulo de autenticación
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Role


class AuthenticationE2ETest(TestCase):
    """Tests E2E para autenticación"""
    
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name="Test Role")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "address": "Test Address"
        }
    
    def test_user_registration_success(self):
        """Test registro exitoso de usuario"""
        url = reverse('user-register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        
        # Verificar que el usuario se creó en la base de datos
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
    
    def test_user_registration_password_mismatch(self):
        """Test registro fallido por contraseñas diferentes"""
        self.user_data['password_confirm'] = 'differentpass'
        url = reverse('user-register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_registration_duplicate_email(self):
        """Test registro fallido por email duplicado"""
        # Crear usuario primero
        User.objects.create_user(
            username="existinguser",
            email=self.user_data['email'],
            password="existingpass"
        )
        
        url = reverse('user-register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Test login exitoso"""
        # Crear usuario primero
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        url = reverse('user-login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login fallido con credenciales inválidas"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        }
        
        url = reverse('user-login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_access_with_token(self):
        """Test acceso al perfil con token válido"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        login_url = reverse('user-login')
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        
        # Acceder al perfil con token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['username'], self.user_data['username'])
    
    def test_user_profile_access_without_token(self):
        """Test acceso al perfil sin token"""
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_update(self):
        """Test actualización del perfil"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        login_url = reverse('user-login')
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        
        # Actualizar perfil
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+9876543210"
        }
        
        update_url = reverse('user-update-profile')
        response = self.client.put(update_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Updated")
        self.assertEqual(response.data['last_name'], "Name")
        self.assertEqual(response.data['phone'], "+9876543210")
    
    def test_change_password(self):
        """Test cambio de contraseña"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        login_url = reverse('user-login')
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        
        # Cambiar contraseña
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        password_data = {
            "old_password": self.user_data['password'],
            "new_password": "newpass123",
            "new_password_confirm": "newpass123"
        }
        
        password_url = reverse('user-change-password')
        response = self.client.post(password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la nueva contraseña funciona
        new_login_data = {
            "email": self.user_data['email'],
            "password": "newpass123"
        }
        
        new_login_response = self.client.post(login_url, new_login_data, format='json')
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)
    
    def test_logout(self):
        """Test logout"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        login_url = reverse('user-login')
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access_token']
        refresh_token = login_response.data['refresh_token']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_data = {"refresh_token": refresh_token}
        
        logout_url = reverse('user-logout')
        response = self.client.post(logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
