"""API regression tests for purchase invoice creation."""
from decimal import Decimal
from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Role
from inventory.models import Category, Product
from purchases.models import Supplier, PurchaseInvoice


class PurchaseInvoiceCreateAPITest(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="Administrator")
        self.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=role,
        )
        self.supplier = Supplier.objects.create(
            name="Prov",
            email="p@test.com",
            phone="123",
            address="Addr",
        )
        category = Category.objects.create(name="Cat")
        self.product = Product.objects.create(
            name="Prod",
            sku="P-1",
            category=category,
            price=Decimal("50.00"),
            stock_quantity=10,
            created_by=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("purchaseinvoice-list")

    def test_create_with_string_unit_price_and_qty_gt_1(self):
        payload = {
            "supplier_id": self.supplier.id,
            "invoice_date": date.today().isoformat(),
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "50.00",
                }
            ],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(Decimal(response.data["amount"]), Decimal("100.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 12)
        invoice = PurchaseInvoice.objects.get(id=response.data["id"])
        self.assertEqual(invoice.items.count(), 1)
