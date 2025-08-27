# Documentación de Modelos - Mini ERP

Este documento describe todos los modelos del sistema Mini ERP, su propósito, relaciones y funcionalidades principales.

## Índice

1. [Módulo de Usuarios](#módulo-de-usuarios)
2. [Módulo de Inventario](#módulo-de-inventario)
3. [Módulo de Compras](#módulo-de-compras)
4. [Módulo de Ventas](#módulo-de-ventas)
5. [Módulo de Reportes](#módulo-de-reportes)

---

## Módulo de Usuarios

### Role
**Propósito**: Define roles de usuario para control de acceso y permisos.

**Campos principales**:
- `name`: Nombre del rol (ej: "Admin", "Vendedor", "Contador")
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

**Funcionalidades**:
- Permite asignar permisos específicos a grupos de usuarios
- Facilita el control de acceso basado en roles

**Relaciones**:
- `User` (Muchos a Uno): Un rol puede tener múltiples usuarios

### User
**Propósito**: Extiende el modelo de usuario de Django para incluir funcionalidades específicas del ERP.

**Campos principales**:
- `username`: Nombre de usuario único
- `email`: Email único del usuario
- `first_name`, `last_name`: Nombre y apellido
- `role`: Relación con el modelo Role
- `is_active`: Estado activo/inactivo del usuario
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Autenticación y autorización
- Gestión de perfiles de usuario
- Control de acceso basado en roles

**Relaciones**:
- `Role` (Muchos a Uno): Cada usuario tiene un rol asignado
- `SaleOrder` (Uno a Muchos): Usuario que creó la orden de venta
- `Product` (Uno a Muchos): Usuario que creó el producto

---

## Módulo de Inventario

### Category
**Propósito**: Organiza productos en categorías para facilitar la gestión y búsqueda.

**Campos principales**:
- `name`: Nombre de la categoría
- `description`: Descripción opcional
- `is_active`: Estado activo/inactivo
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Clasificación de productos
- Filtrado y organización del inventario
- Reportes por categoría

**Relaciones**:
- `Product` (Uno a Muchos): Una categoría puede tener múltiples productos

### Product
**Propósito**: Representa los productos/servicios que se venden y compran en el sistema.

**Campos principales**:
- `name`: Nombre del producto
- `sku`: Código único del producto (Stock Keeping Unit)
- `category`: Categoría del producto
- `description`: Descripción detallada
- `price`: Precio de venta
- `cost_price`: Precio de costo
- `stock_quantity`: Cantidad en stock
- `min_stock_level`: Nivel mínimo de stock para alertas
- `is_active`: Estado activo/inactivo
- `created_by`: Usuario que creó el producto
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión de inventario en tiempo real
- Control de stock mínimo
- Cálculo de valor de inventario
- Trazabilidad de productos

**Relaciones**:
- `Category` (Muchos a Uno): Cada producto pertenece a una categoría
- `User` (Muchos a Uno): Usuario que creó el producto
- `StockMovement` (Uno a Muchos): Movimientos de stock del producto
- `SaleOrderItem` (Uno a Muchos): Items de venta que usan este producto
- `PurchaseInvoiceItem` (Uno a Muchos): Items de compra que usan este producto

### StockMovement
**Propósito**: Registra todos los movimientos de stock para mantener trazabilidad completa del inventario.

**Campos principales**:
- `product`: Producto afectado
- `movement_type`: Tipo de movimiento ('in', 'out', 'return', 'adjustment')
- `quantity`: Cantidad movida
- `previous_quantity`: Stock antes del movimiento
- `new_quantity`: Stock después del movimiento
- `reference`: Referencia del movimiento (orden, factura, etc.)
- `notes`: Notas adicionales
- `created_at`: Timestamp del movimiento

**Funcionalidades**:
- Trazabilidad completa del inventario
- Auditoría de movimientos de stock
- Prevención de stock negativo
- Historial de cambios de inventario

**Relaciones**:
- `Product` (Muchos a Uno): Producto afectado por el movimiento

---

## Módulo de Compras

### Supplier
**Propósito**: Gestiona la información de proveedores para las compras.

**Campos principales**:
- `name`: Nombre del proveedor
- `email`: Email de contacto
- `phone`: Teléfono de contacto
- `address`: Dirección del proveedor
- `contact_person`: Persona de contacto
- `is_active`: Estado activo/inactivo
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión de información de proveedores
- Contacto y comunicación
- Reportes de compras por proveedor

**Relaciones**:
- `PurchaseInvoice` (Uno a Muchos): Facturas de compra del proveedor

### PurchaseInvoice
**Propósito**: Representa las facturas de compra que aumentan el inventario.

**Campos principales**:
- `invoice_number`: Número único de factura (auto-generado)
- `supplier`: Proveedor que emitió la factura
- `invoice_date`: Fecha de la factura
- `due_date`: Fecha de vencimiento
- `amount`: Monto total de la factura
- `paid_amount`: Monto pagado
- `status`: Estado ('pending', 'partial', 'paid', 'overdue')
- `notes`: Notas adicionales
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión de facturas de compra
- Control de pagos a proveedores
- Actualización automática de inventario
- Generación automática de números de factura

**Relaciones**:
- `Supplier` (Muchos a Uno): Proveedor que emitió la factura
- `PurchaseInvoiceItem` (Uno a Muchos): Items de la factura

### PurchaseInvoiceItem
**Propósito**: Representa los items individuales de una factura de compra.

**Campos principales**:
- `invoice`: Factura a la que pertenece
- `product`: Producto comprado
- `quantity`: Cantidad comprada
- `unit_price`: Precio unitario
- `total_price`: Precio total (calculado automáticamente)
- `created_at`: Timestamp de creación

**Funcionalidades**:
- Detalle de productos en facturas de compra
- Cálculo automático de totales
- Actualización automática de inventario al crear
- Actualización del monto total de la factura

**Relaciones**:
- `PurchaseInvoice` (Muchos a Uno): Factura a la que pertenece
- `Product` (Muchos a Uno): Producto comprado

---

## Módulo de Ventas

### Customer
**Propósito**: Gestiona la información de clientes para las ventas.

**Campos principales**:
- `name`: Nombre del cliente
- `email`: Email de contacto
- `phone`: Teléfono de contacto
- `address`: Dirección del cliente
- `is_active`: Estado activo/inactivo
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión de información de clientes
- Contacto y comunicación
- Reportes de ventas por cliente

**Relaciones**:
- `SaleOrder` (Uno a Muchos): Órdenes de venta del cliente

### SaleOrder
**Propósito**: Representa las órdenes de venta que pueden disminuir el inventario.

**Campos principales**:
- `order_number`: Número único de orden (auto-generado)
- `customer`: Cliente que realizó la orden
- `status`: Estado ('draft', 'confirmed', 'shipped', 'delivered', 'cancelled')
- `order_date`: Fecha de la orden
- `delivery_date`: Fecha de entrega
- `subtotal`: Subtotal de la orden
- `tax_amount`: Monto de impuestos
- `total_amount`: Monto total
- `notes`: Notas adicionales
- `created_by`: Usuario que creó la orden
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión del ciclo de vida de órdenes de venta
- Cálculo automático de totales e impuestos
- Control de stock al confirmar órdenes
- Generación automática de números de orden
- Estados de orden (borrador → confirmada → enviada → entregada)

**Relaciones**:
- `Customer` (Muchos a Uno): Cliente que realizó la orden
- `User` (Muchos a Uno): Usuario que creó la orden
- `SaleOrderItem` (Uno a Muchos): Items de la orden
- `Invoice` (Uno a Uno): Factura asociada a la orden

### SaleOrderItem
**Propósito**: Representa los items individuales de una orden de venta.

**Campos principales**:
- `order`: Orden a la que pertenece
- `product`: Producto vendido
- `quantity`: Cantidad vendida
- `unit_price`: Precio unitario
- `total_price`: Precio total (calculado automáticamente)
- `created_at`: Timestamp de creación

**Funcionalidades**:
- Detalle de productos en órdenes de venta
- Cálculo automático de totales
- Actualización automática de totales de la orden

**Relaciones**:
- `SaleOrder` (Muchos a Uno): Orden a la que pertenece
- `Product` (Muchos a Uno): Producto vendido

### Invoice
**Propósito**: Representa las facturas de venta para el cobro a clientes.

**Campos principales**:
- `invoice_number`: Número único de factura (auto-generado)
- `sale_order`: Orden de venta asociada
- `invoice_date`: Fecha de la factura
- `due_date`: Fecha de vencimiento
- `amount`: Monto total de la factura
- `paid_amount`: Monto cobrado
- `status`: Estado ('pending', 'partial', 'paid', 'overdue')
- `created_at`, `updated_at`: Timestamps

**Funcionalidades**:
- Gestión de facturas de venta
- Control de cobros a clientes
- Generación automática de números de factura
- Estados de factura basados en pagos

**Relaciones**:
- `SaleOrder` (Uno a Uno): Orden de venta asociada

---

## Módulo de Reportes

El módulo de reportes no tiene modelos propios, sino que utiliza los datos de los otros módulos para generar reportes y estadísticas.

**Funcionalidades principales**:
- Dashboard con resumen general
- Reportes de ventas por período
- Reportes de inventario y stock
- Reportes financieros
- Reportes de clientes y proveedores
- Análisis de rentabilidad

---

## Flujo de Negocio

### Flujo de Compra
1. **Crear Factura de Compra** (`PurchaseInvoice`)
   - Se crea la factura con items (`PurchaseInvoiceItem`)
   - Al crear items, se actualiza automáticamente el stock del producto
   - Se calcula el monto total de la factura

### Flujo de Venta
1. **Crear Orden de Venta** (`SaleOrder`)
   - Se crea la orden con items (`SaleOrderItem`)
   - Estado inicial: 'draft'
   - Se calculan totales e impuestos

2. **Confirmar Orden** (`SaleOrder.confirm()`)
   - Se verifica stock disponible
   - Se actualiza el stock (disminuye)
   - Estado cambia a 'confirmed'

3. **Enviar y Entregar**
   - Estados: 'shipped' → 'delivered'
   - Para reportes, solo las órdenes 'delivered' se consideran ventas completadas

4. **Generar Factura** (`Invoice`)
   - Se crea la factura asociada a la orden
   - Se gestiona el cobro al cliente

### Control de Inventario
- **Entrada de Stock**: Al crear `PurchaseInvoiceItem`
- **Salida de Stock**: Al confirmar `SaleOrder`
- **Trazabilidad**: Todos los movimientos se registran en `StockMovement`
- **Prevención**: No se permite stock negativo

---

## Consideraciones de Diseño

### Ventajas del Diseño Actual
1. **Simplicidad**: Flujo directo sin órdenes de compra intermedias
2. **Trazabilidad**: Todos los movimientos están registrados
3. **Integridad**: Validaciones para prevenir inconsistencias
4. **Flexibilidad**: Estados de orden permiten diferentes flujos de trabajo

### Limitaciones
1. **Sin Órdenes de Compra**: No hay flujo de aprobación de compras
2. **Sin Devoluciones**: No hay manejo explícito de devoluciones
3. **Sin Múltiples Almacenes**: Solo un almacén por producto

### Posibles Mejoras Futuras
1. Agregar órdenes de compra con flujo de aprobación
2. Implementar sistema de devoluciones
3. Agregar múltiples almacenes
4. Implementar sistema de descuentos y promociones
5. Agregar gestión de lotes y fechas de vencimiento
