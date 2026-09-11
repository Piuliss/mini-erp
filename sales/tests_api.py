"""API regression tests for sale order creation."""
from decimal import Decimal
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Role
from inventory.models import Category, Product
from sales.models import Customer, SaleOrder


class SaleOrderCreateAPITest(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="Administrator")
        self.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=role,
        )
        self.customer = Customer.objects.create(name="Cliente", email="c@test.com")
        category = Category.objects.create(name="Cat")
        self.product = Product.objects.create(
            name="Prod",
            sku="P-1",
            category=category,
            price=Decimal("120.00"),
            stock_quantity=50,
            created_by=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("saleorder-list")

    def test_create_with_string_unit_price_and_qty_gt_1(self):
        """Swagger often sends unit_price as string; qty*str must not repeat."""
        payload = {
            "customer_id": self.customer.id,
            "order_date": date.today().isoformat(),
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "120.00",
                }
            ],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(Decimal(response.data["items"][0]["total_price"]), Decimal("240.00"))
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("240.00"))
        self.assertEqual(Decimal(response.data["total_amount"]), Decimal("264.00"))
        order = SaleOrder.objects.get(id=response.data["id"])
        self.assertEqual(order.items.count(), 1)

    def test_create_rejects_empty_items(self):
        payload = {
            "customer_id": self.customer.id,
            "order_date": date.today().isoformat(),
            "items": [],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
