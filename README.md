# Mini ERP - Django REST Framework API

Un sistema ERP completo construido con Django REST Framework, diseñado para que los estudiantes desarrollen aplicaciones frontend.

## 🚀 Características

- **Autenticación JWT**: Sistema de autenticación seguro con tokens
- **Gestión de Usuarios y Roles**: Control de acceso basado en roles
- **Inventario**: Gestión completa de productos y stock
- **Ventas**: Órdenes de venta, clientes e facturación
- **Compras**: Órdenes de compra, proveedores y gestión de pagos
- **Reportes**: Sistema completo de reportes y estadísticas
- **Documentación API**: Swagger/OpenAPI integrado
- **Datos de Prueba**: Fixtures con datos de ejemplo

## 🛠️ Tecnologías

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Autenticación**: JWT (djangorestframework-simplejwt)
- **Base de Datos**: PostgreSQL (con fallback a SQLite)
- **Documentación**: drf-yasg (Swagger/OpenAPI)
- **CORS**: django-cors-headers
- **Contenedorización**: Docker & Docker Compose

## 📋 Requisitos

- Python 3.9+
- Docker y Docker Compose (recomendado)
- PostgreSQL (opcional, SQLite por defecto)

## ⚡ Inicio Rápido (5 minutos)

### 1. Clonar y Configurar
```bash
git clone <repository-url>
cd mini-erp

# Crear archivo .env para desarrollo
cp env.example .env

# Configurar entorno
python scripts_utils/manage_dev.py setup
```

### 2. Iniciar Servidor
```bash
python scripts_utils/manage_dev.py run
```

### 3. Acceder a la API
- **Documentación**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

> 📖 Para instalación completa, troubleshooting y detalles técnicos, consulta [DEVELOPMENT.md](DEVELOPMENT.md)

## 🚀 Comandos de Producción

> 📖 Para comandos de gestión de Docker, troubleshooting y diagnóstico, consulta [DEVELOPMENT.md](DEVELOPMENT.md)

## 🧪 Pruebas con cURL (Producción)

### Configuración Base
```bash
# URL base de producción
BASE_URL="http://185.218.124.154:8800"

# Headers comunes
HEADERS="-H 'Content-Type: application/json'"
```

### Verificación Básica de Conectividad
```bash
# 1. Probar endpoint raíz (debería devolver 404, pero confirmar que Django responde)
curl -v $BASE_URL/

# 2. Probar documentación de la API
curl -v $BASE_URL/api/docs/

# 3. Probar endpoint de productos (sin autenticación, debería devolver 401)
curl -v $BASE_URL/api/inventory/products/

# 4. Probar admin de Django
curl -v $BASE_URL/admin/
```

### Diagnóstico Rápido
```bash
# Verificar configuración de red
curl -v $BASE_URL/api/docs/ 2>&1 | grep -E "(HTTP|Connected|Failed)"

# Verificar si el puerto está abierto
telnet 185.218.124.154 8800

# Diagnóstico de autenticación
echo "=== DIAGNÓSTICO DE AUTENTICACIÓN ==="
echo "1. Verificando documentación de la API..."
curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/docs/

echo -e "\n2. Verificando endpoint de login..."
curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/users/users/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email": "test@test.com", "password": "test"}'

echo -e "\n3. Verificando endpoint de productos (sin auth)..."
curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/inventory/products/

echo -e "\n4. Verificando admin de Django..."
curl -s -o /dev/null -w "%{http_code}" $BASE_URL/admin/

echo -e "\n=== FIN DEL DIAGNÓSTICO ==="
```

### Autenticación
```bash
# 1. Login y obtener token
TOKEN=$(curl -s -X POST $BASE_URL/api/users/users/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@minierp.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Verificar token
curl -X GET $BASE_URL/api/users/users/profile/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 3. Logout
curl -X POST $BASE_URL/api/users/users/logout/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"refresh_token": "your_refresh_token"}'
```

### Productos
```bash
# 1. Listar productos
curl -X GET $BASE_URL/api/inventory/products/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 2. Obtener un producto específico
curl -X GET $BASE_URL/api/inventory/products/1/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 3. Crear un producto
curl -X POST $BASE_URL/api/inventory/products/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Nuevo Producto",
    "description": "Descripción del producto",
    "sku": "PROD-001",
    "category": 1,
    "price": "99.99",
    "cost_price": "50.00",
    "stock_quantity": 100,
    "min_stock_level": 10,
    "max_stock_level": 500
  }'

# 4. Productos con bajo stock
curl -X GET $BASE_URL/api/inventory/products/low_stock/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"
```

### Categorías
```bash
# 1. Listar categorías
curl -X GET $BASE_URL/api/inventory/categories/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 2. Crear categoría
curl -X POST $BASE_URL/api/inventory/categories/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Nueva Categoría",
    "description": "Descripción de la categoría"
  }'
```

### Clientes
```bash
# 1. Listar clientes
curl -X GET $BASE_URL/api/sales/customers/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 2. Crear cliente
curl -X POST $BASE_URL/api/sales/customers/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+1234567890",
    "address": "Calle Principal 123"
  }'
```

### Órdenes de Venta
```bash
# 1. Listar órdenes
curl -X GET $BASE_URL/api/sales/orders/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 2. Crear orden de venta
curl -X POST $BASE_URL/api/sales/orders/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer": 1,
    "order_date": "2024-01-15",
    "delivery_date": "2024-01-20",
    "notes": "Orden de prueba",
    "items": [
      {
        "product": 1,
        "quantity": 2,
        "unit_price": "99.99"
      }
    ]
  }'

# 3. Confirmar orden
curl -X POST $BASE_URL/api/sales/orders/1/confirm/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"
```

### Reportes
```bash
# 1. Dashboard summary
curl -X GET $BASE_URL/api/reports/dashboard_summary/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 2. Reporte de ventas
curl -X GET $BASE_URL/api/reports/sales_report/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"

# 3. Reporte de inventario
curl -X GET $BASE_URL/api/reports/inventory_report/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"
```


### Notas Importantes
- **URL de Producción**: `http://185.218.124.154:8800` (fija para todas las pruebas)
- **Reemplaza `$TOKEN`** con el token obtenido del login
- **Instala `jq`** para mejor formato de respuesta: `brew install jq` (macOS) o `apt install jq` (Ubuntu)
- **Los IDs** (como `/1/`) pueden variar según los datos existentes en producción
- **Credenciales de prueba**: 
  - **Email**: `admin@minierp.com`
  - **Password**: `test123456`
- **Verificar usuarios disponibles**: Si las credenciales no funcionan, verifica que los datos de prueba se hayan cargado en producción
- **Todas las pruebas**: Están configuradas para ejecutarse directamente contra el servidor de producción

### Credenciales de Prueba

**✅ CONFIRMADO: Las siguientes credenciales funcionan en producción:**

| Usuario | Email | Contraseña | Rol |
|---------|-------|------------|-----|
| admin | admin@minierp.com | test123456 | Administrador |
| manager | manager@minierp.com | test123456 | Manager |
| sales | sales@minierp.com | test123456 | Ventas |

**Nota**: Si las credenciales no funcionan, ejecuta este comando en el servidor:
```bash
docker exec -it mini-erp-web-1 python manage.py shell -c "
from users.models import User
for user in User.objects.all():
    user.set_password('test123456')
    user.save()
    print(f'Contraseña actualizada para {user.email}')
"
```

## 📚 Endpoints Principales

### Usuarios y Autenticación
- `POST /api/users/users/register/` - Registro de usuario
- `POST /api/users/users/login/` - Login
- `GET /api/users/users/profile/` - Perfil del usuario
- `PUT /api/users/users/update_profile/` - Actualizar perfil
- `POST /api/users/users/change_password/` - Cambiar contraseña
- `POST /api/users/users/logout/` - Logout

### Inventario
- `GET /api/inventory/products/` - Listar productos
- `POST /api/inventory/products/` - Crear producto
- `GET /api/inventory/categories/` - Listar categorías
- `GET /api/inventory/products/low_stock/` - Productos con bajo stock
- `GET /api/inventory/products/stock_summary/` - Resumen de inventario

### Ventas
- `GET /api/sales/customers/` - Listar clientes
- `POST /api/sales/orders/` - Crear orden de venta
- `GET /api/sales/orders/` - Listar órdenes
- `POST /api/sales/orders/{id}/confirm/` - Confirmar orden
- `GET /api/sales/orders/sales_summary/` - Resumen de ventas

### Compras
- `GET /api/purchases/suppliers/` - Listar proveedores
- `POST /api/purchases/orders/` - Crear orden de compra
- `GET /api/purchases/orders/` - Listar órdenes
- `POST /api/purchases/orders/{id}/receive/` - Recibir orden

### Reportes
- `GET /api/reports/dashboard_summary/` - Resumen del dashboard
- `GET /api/reports/sales_report/` - Reporte de ventas
- `GET /api/reports/inventory_report/` - Reporte de inventario
- `GET /api/reports/financial_report/` - Reporte financiero

## 📖 Documentación de la API

La documentación completa está disponible públicamente en:
- **Swagger UI**: http://185.218.124.154:8800/api/docs/
- **ReDoc**: http://185.218.124.154:8800/api/redoc/


## 🎯 Casos de Uso para Estudiantes

### Frontend Development
1. **Dashboard**: Crear un dashboard con estadísticas principales
2. **CRUD Operations**: Implementar operaciones CRUD para cada módulo
3. **Authentication**: Integrar sistema de login/logout
4. **Real-time Updates**: Implementar actualizaciones en tiempo real
5. **Reports**: Crear visualizaciones de reportes
6. **Responsive Design**: Diseño responsive para móviles

### Librerías Útiles
- **UI Components**: Material-UI, Ant Design, Chakra UI
- **Charts**: Chart.js, D3.js, Recharts
- **State Management**: Redux, Zustand, Pinia
- **HTTP Client**: Axios, React Query, SWR

## 🎯 Ejercicios para Estudiantes

### Nivel Básico
1. **Login/Logout**: Implementar autenticación
2. **Lista de Productos**: Mostrar productos con paginación
3. **Dashboard**: Crear dashboard con estadísticas básicas

### Nivel Intermedio
1. **CRUD Completo**: Crear, editar, eliminar productos
2. **Filtros y Búsqueda**: Implementar filtros por categoría, precio
3. **Gestión de Stock**: Mostrar alertas de bajo stock

### Nivel Avanzado
1. **Órdenes de Venta**: Crear y gestionar órdenes
2. **Reportes Visuales**: Gráficos y estadísticas
3. **Notificaciones**: Alertas en tiempo real

## 📖 Recursos de Aprendizaje

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Swagger/OpenAPI](https://swagger.io/)


**¡Disfruta desarrollando tu frontend con este Mini ERP! 🚀**

> 📖 Para información detallada sobre instalación, configuración, troubleshooting y desarrollo, consulta [DEVELOPMENT.md](DEVELOPMENT.md)