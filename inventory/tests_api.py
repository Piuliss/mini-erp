"""API tests for inventory stock adjustments."""
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Role
from inventory.models import Category, Product


class AdjustStockAPITest(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="Administrator")
        self.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=role,
        )
        category = Category.objects.create(name="Cat")
        self.product = Product.objects.create(
            name="Prod",
            sku="P-1",
            category=category,
            price=Decimal("10.00"),
            cost_price=Decimal("4.00"),
            stock_quantity=10,
            created_by=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("product-adjust-stock", kwargs={"pk": self.product.id})

    def test_adjust_stock_accepts_string_quantity(self):
        response = self.client.post(
            self.url,
            {"quantity": "3", "movement_type": "in", "notes": "string qty"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 13)

    def test_adjust_stock_rejects_invalid_quantity(self):
        response = self.client.post(
            self.url,
            {"quantity": "abc", "movement_type": "in"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
