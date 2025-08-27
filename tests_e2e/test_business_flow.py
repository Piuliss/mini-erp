"""
Tests End-to-End para flujo completo de negocio
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from users.models import User, Role
from inventory.models import Category, Product
from purchases.models import Supplier, PurchaseInvoice, PurchaseInvoiceItem
from sales.models import Customer, SaleOrder, SaleOrderItem



class BusinessFlowE2ETest(TestCase):
    """Tests E2E para flujo completo de negocio"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear roles
        self.admin_role = Role.objects.create(name="Administrator")
        self.supplier_role = Role.objects.create(name="Supplier")
        
        # Crear usuario admin
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            role=self.admin_role
        )
        
        # Crear categoría
        self.category = Category.objects.create(
            name="Electrónicos",
            description="Productos electrónicos"
        )
        
        # Crear producto inicial
        self.product = Product.objects.create(
            name="Laptop Test",
            description="Laptop para testing",
            sku="LAP-001",
            category=self.category,
            price=Decimal('999.99'),
            cost_price=Decimal('600.00'),
            stock_quantity=10,
            min_stock_level=5,
            max_stock_level=50,
            created_by=self.admin_user
        )
        
        # Crear proveedor
        self.supplier = Supplier.objects.create(
            name="Proveedor Test",
            email="proveedor@test.com",
            phone="+1234567890",
            address="Dirección del proveedor"
        )
        
        # Crear cliente
        self.customer = Customer.objects.create(
            name="Cliente Test",
            email="cliente@test.com",
            phone="+0987654321",
            address="Dirección del cliente"
        )
        
        # Autenticar como admin
        login_data = {
            "email": "admin@test.com",
            "password": "testpass123"
        }
        login_url = reverse('user-login')
        login_response = self.client.post(login_url, login_data, format='json')
        self.token = login_response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_complete_business_flow(self):
        """
        Test E2E completo:
        1. Crear factura de compra que aumente el stock directamente
        2. Crear orden de venta que disminuya el stock
        3. Verificar reporte de ventas del día
        """
        initial_stock = self.product.stock_quantity
        
        # PASO 1: Crear factura de compra directamente (esto aumenta el stock)
        print(f"📦 Stock inicial: {initial_stock}")
        
        purchase_invoice_data = {
            "supplier_id": self.supplier.id,
            "invoice_date": date.today().isoformat(),
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Factura de compra para testing E2E",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 20,
                    "unit_price": 580.00
                }
            ]
        }
        
        invoice_url = reverse('purchaseinvoice-list')
        invoice_response = self.client.post(invoice_url, purchase_invoice_data, format='json')
        
        print(f"🔍 Invoice response status: {invoice_response.status_code}")
        print(f"🔍 Invoice response data: {invoice_response.data}")
        
        self.assertEqual(invoice_response.status_code, status.HTTP_201_CREATED)
        invoice_id = invoice_response.data['id']
        print(f"✅ Factura de compra creada: ID {invoice_id}")
        
        # Verificar que el stock aumentó (la factura debería actualizar el stock)
        self.product.refresh_from_db()
        stock_after_purchase = self.product.stock_quantity
        expected_stock_after_purchase = initial_stock + 20
        print(f"📦 Stock después de compra: {stock_after_purchase} (esperado: {expected_stock_after_purchase})")
        
        # Verificar que los items se crearon
        from purchases.models import PurchaseInvoiceItem
        items_count = PurchaseInvoiceItem.objects.filter(invoice_id=invoice_id).count()
        print(f"🔍 Items creados: {items_count}")
        
        # Verificar el item específico
        item = PurchaseInvoiceItem.objects.filter(invoice_id=invoice_id).first()
        if item:
            print(f"🔍 Item: {item.product.name}, cantidad: {item.quantity}, precio: {item.unit_price}")
            print(f"🔍 Producto stock antes: {item.product.stock_quantity}")
            item.product.refresh_from_db()
            print(f"🔍 Producto stock después: {item.product.stock_quantity}")
        
        self.assertEqual(stock_after_purchase, expected_stock_after_purchase)
        
        # PASO 3: Crear orden de venta
        sale_order_data = {
            "customer_id": self.customer.id,
            "order_date": date.today().isoformat(),
            "delivery_date": (date.today() + timedelta(days=3)).isoformat(),
            "notes": "Orden de venta para testing E2E",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 5,
                    "unit_price": 999.99
                }
            ]
        }
        
        sale_url = reverse('saleorder-list')
        sale_response = self.client.post(sale_url, sale_order_data, format='json')
        
        self.assertEqual(sale_response.status_code, status.HTTP_201_CREATED)
        sale_order_id = sale_response.data['id']
        print(f"✅ Orden de venta creada: ID {sale_order_id}")
        
        # Verificar que la orden se creó correctamente
        self.assertEqual(sale_response.data['customer_id'], self.customer.id)
        # Los items se crean pero no se devuelven en la respuesta del serializer
        # Vamos a verificar que se crearon consultando la base de datos
        from sales.models import SaleOrder
        order = SaleOrder.objects.get(id=sale_order_id)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 5)
        
        # PASO 4: Confirmar la orden de venta (esto disminuye el stock)
        confirm_url = reverse('saleorder-confirm', kwargs={'pk': sale_order_id})
        confirm_response = self.client.post(confirm_url, {}, format='json')
        
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        print(f"✅ Orden de venta confirmada")
        
        # Marcar como enviada y entregada para que aparezca en el reporte
        ship_url = reverse('saleorder-ship', kwargs={'pk': sale_order_id})
        ship_response = self.client.post(ship_url, {}, format='json')
        self.assertEqual(ship_response.status_code, status.HTTP_200_OK)
        
        deliver_url = reverse('saleorder-deliver', kwargs={'pk': sale_order_id})
        deliver_response = self.client.post(deliver_url, {}, format='json')
        self.assertEqual(deliver_response.status_code, status.HTTP_200_OK)
        print(f"✅ Orden de venta marcada como entregada")
        
        # Verificar que el stock disminuyó
        self.product.refresh_from_db()
        stock_after_sale = self.product.stock_quantity
        expected_stock_after_sale = stock_after_purchase - 5
        self.assertEqual(stock_after_sale, expected_stock_after_sale)
        print(f"📦 Stock después de venta: {stock_after_sale} (esperado: {expected_stock_after_sale})")
        
        # PASO 5: Verificar reporte de ventas del día
        sales_report_url = reverse('report-sales-report')
        report_response = self.client.get(sales_report_url, format='json')
        
        self.assertEqual(report_response.status_code, status.HTTP_200_OK)
        print(f"✅ Reporte de ventas obtenido")
        
        # Verificar que el reporte contiene la información esperada
        report_data = report_response.data
        self.assertIn('summary', report_data)
        self.assertIn('total_sales', report_data['summary'])
        self.assertIn('total_orders', report_data['summary'])
        
        # Verificar que hay al menos una venta en el día
        summary = report_data['summary']
        self.assertGreater(summary['total_orders'], 0)
        
        print(f"📊 Reporte de ventas: {summary}")
        print(f"📊 Total ventas: ${summary['total_sales']}")
        print(f"📊 Total órdenes: {summary['total_orders']}")
        
        # PASO 6: Verificar resumen final
        print(f"\n🎯 RESUMEN DEL FLUJO:")
        print(f"   Stock inicial: {initial_stock}")
        print(f"   Compra: +20 unidades")
        print(f"   Venta: -5 unidades")
        print(f"   Stock final: {stock_after_sale}")
        print(f"   Ventas del día: ${summary['total_sales']}")
        
        # Verificaciones finales
        self.assertEqual(stock_after_sale, initial_stock + 20 - 5)
        self.assertGreater(Decimal(summary['total_sales']), Decimal('0'))
    
    def test_stock_validation_in_business_flow(self):
        """Test que verifica que no se puede vender más stock del disponible"""
        # Intentar vender más stock del disponible
        sale_order_data = {
            "customer_id": self.customer.id,
            "order_date": date.today().isoformat(),
            "delivery_date": (date.today() + timedelta(days=3)).isoformat(),
            "notes": "Orden de venta con stock insuficiente",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 999,  # Más stock del disponible
                    "unit_price": 999.99
                }
            ]
        }
        
        sale_url = reverse('saleorder-list')
        sale_response = self.client.post(sale_url, sale_order_data, format='json')
        
        # La orden se puede crear, pero no confirmar
        self.assertEqual(sale_response.status_code, status.HTTP_201_CREATED)
        sale_order_id = sale_response.data['id']
        
        # Intentar confirmar la orden (debería fallar)
        confirm_url = reverse('saleorder-confirm', kwargs={'pk': sale_order_id})
        confirm_response = self.client.post(confirm_url, {}, format='json')
        
        # Debería fallar por stock insuficiente
        self.assertNotEqual(confirm_response.status_code, status.HTTP_200_OK)
        print(f"✅ Validación de stock funciona: no se puede confirmar orden con stock insuficiente")
    
    def test_inventory_tracking_in_business_flow(self):
        """Test que verifica el tracking de inventario durante el flujo"""
        initial_stock = self.product.stock_quantity
        
        # Crear factura de compra directamente
        purchase_invoice_data = {
            "supplier_id": self.supplier.id,
            "invoice_date": date.today().isoformat(),
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Factura para tracking de inventario",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 10,
                    "unit_price": 580.00
                }
            ]
        }
        
        invoice_url = reverse('purchaseinvoice-list')
        invoice_response = self.client.post(invoice_url, purchase_invoice_data, format='json')
        invoice_id = invoice_response.data['id']
        
        # Verificar stock después de compra
        self.product.refresh_from_db()
        stock_after_purchase = self.product.stock_quantity
        
        # Crear y confirmar orden de venta
        sale_order_data = {
            "customer_id": self.customer.id,
            "order_date": date.today().isoformat(),
            "delivery_date": (date.today() + timedelta(days=3)).isoformat(),
            "notes": "Orden para tracking de inventario",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 3,
                    "unit_price": 999.99
                }
            ]
        }
        
        sale_url = reverse('saleorder-list')
        sale_response = self.client.post(sale_url, sale_order_data, format='json')
        sale_order_id = sale_response.data['id']
        
        # Confirmar la orden
        confirm_url = reverse('saleorder-confirm', kwargs={'pk': sale_order_id})
        self.client.post(confirm_url, {}, format='json')
        
        # Verificar stock final
        self.product.refresh_from_db()
        final_stock = self.product.stock_quantity
        
        # Verificar que el tracking es correcto
        expected_final_stock = initial_stock + 10 - 3
        self.assertEqual(final_stock, expected_final_stock)
        print(f"✅ Tracking de inventario correcto: {initial_stock} + 10 - 3 = {final_stock}")
        
        # Verificar que el producto no está en bajo stock
        low_stock_url = reverse('product-low-stock')
        low_stock_response = self.client.get(low_stock_url, format='json')
        
        self.assertEqual(low_stock_response.status_code, status.HTTP_200_OK)
        low_stock_products = low_stock_response.data
        
        # Nuestro producto no debería estar en bajo stock
        product_in_low_stock = any(p['id'] == self.product.id for p in low_stock_products)
        self.assertFalse(product_in_low_stock, "Producto no debería estar en bajo stock")
