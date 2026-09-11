"""API tests for report endpoints that previously returned 500."""
from decimal import Decimal
from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, Role
from inventory.models import Category, Product
from sales.models import Customer, SaleOrder, Invoice
from purchases.models import Supplier, PurchaseInvoice


class ReportsAPITest(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="Administrator")
        self.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=role,
        )
        self.client.force_authenticate(user=self.user)

        # Product without category and without cost_price (prod data edge case)
        Product.objects.create(
            name="No Cat",
            sku="NC-1",
            price=Decimal("10.00"),
            cost_price=None,
            stock_quantity=2,
            created_by=self.user,
        )
        category = Category.objects.create(name="Cat")
        Product.objects.create(
            name="With Cat",
            sku="WC-1",
            category=category,
            price=Decimal("20.00"),
            cost_price=Decimal("5.00"),
            stock_quantity=3,
            created_by=self.user,
        )

        supplier = Supplier.objects.create(
            name="Prov", email="p@t.com", phone="1", address="a"
        )
        # Orphan purchase with null amount
        PurchaseInvoice.objects.create(
            supplier=supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=None,
        )
        PurchaseInvoice.objects.create(
            supplier=supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=Decimal("100.00"),
        )

        customer = Customer.objects.create(name="Cli", email="c@t.com")
        order = SaleOrder.objects.create(
            customer=customer,
            order_date=date.today(),
            status="delivered",
            total_amount=Decimal("50.00"),
            created_by=self.user,
        )
        Invoice.objects.create(
            sale_order=order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=Decimal("50.00"),
            paid_amount=Decimal("10.00"),
            status="partial",
        )

    def test_dashboard_summary_handles_null_purchase_amount(self):
        url = reverse("report-dashboard-summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("sales", response.data)
        self.assertIn("purchases", response.data)

    def test_inventory_report_handles_null_category_and_cost(self):
        url = reverse("report-inventory-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertGreaterEqual(len(response.data["products"]), 2)

    def test_financial_report_uses_db_balance_expression(self):
        url = reverse("report-financial-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("outstanding_receivables", response.data["revenue"])
        self.assertEqual(
            response.data["revenue"]["outstanding_receivables"], 40.0
        )
