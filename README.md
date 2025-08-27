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
python scripts_utils/manage_dev.py setup
```

### 2. Iniciar Servidor
```bash
python scripts_utils/manage_dev.py run
```

### 3. Acceder a la API
- **Documentación**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

## 🚀 Instalación Completa

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd mini-erp
```

2. **Ejecutar con Docker Compose**
```bash
docker-compose up --build
```

**O usar el script de gestión:**
```bash
python scripts_utils/manage_dev.py docker-setup
```

El sistema estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/api/docs/
- **Documentación ReDoc**: http://localhost:8000/api/redoc/
- **Admin Django**: http://localhost:8000/admin/

### Opción 2: Instalación Local

**Método rápido con script de gestión:**
```bash
python scripts_utils/manage_dev.py setup
```

**O método manual:**

1. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar base de datos**
```bash
python manage.py migrate
```

4. **Cargar datos de prueba**
```bash
python manage.py loaddata fixtures/*.json
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor**
```bash
python manage.py runserver
```

## 🔐 Autenticación

### Registro de Usuario
```bash
POST /api/users/register/
{
    "username": "usuario",
    "email": "usuario@email.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Nombre",
    "last_name": "Apellido"
}
```

### Login
```bash
POST /api/users/login/
{
    "email": "usuario@email.com",
    "password": "password123"
}
```

### Usar Token
```bash
Authorization: Bearer <access_token>
```

## 🧪 Pruebas con cURL

### Configuración Base
```bash
# URL base (ajusta según tu configuración)
BASE_URL="http://localhost:8800"  # Docker Compose
# BASE_URL="http://localhost:8000"  # Desarrollo local

# Headers comunes
HEADERS="-H 'Content-Type: application/json'"
```

### Autenticación
```bash
# 1. Login y obtener token
TOKEN=$(curl -s -X POST $BASE_URL/api/users/users/login/ \
  $HEADERS \
  -d '{
    "email": "admin@minierp.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Verificar token
curl -X GET $BASE_URL/api/users/users/profile/ \
  $HEADERS \
  -H "Authorization: Bearer $TOKEN"

# 3. Logout
curl -X POST $BASE_URL/api/users/users/logout/ \
  $HEADERS \
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

### Script de Prueba Completa
```bash
#!/bin/bash
# Script para probar toda la API

export BASE_URL="http://localhost:8800"

echo "🔐 Iniciando pruebas de la API..."

# Login
echo "1. Login..."
TOKEN=$(curl -s -X POST $BASE_URL/api/users/users/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@minierp.com",
    "password": "test123456"
  }' | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Error en login"
    exit 1
fi

echo "✅ Login exitoso"

# Probar endpoints
echo "2. Probando productos..."
curl -s -X GET $BASE_URL/api/inventory/products/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "3. Probando categorías..."
curl -s -X GET $BASE_URL/api/inventory/categories/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "4. Probando clientes..."
curl -s -X GET $BASE_URL/api/sales/customers/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "5. Probando reportes..."
curl -s -X GET $BASE_URL/api/reports/dashboard_summary/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq '.total_products'

echo "✅ Todas las pruebas completadas"
```

### Notas Importantes
- **Reemplaza `$TOKEN`** con el token obtenido del login
- **Ajusta `$BASE_URL`** según tu configuración (8800 para Docker, 8000 para local)
- **Instala `jq`** para mejor formato de respuesta: `brew install jq` (macOS) o `apt install jq` (Ubuntu)
- **Los IDs** (como `/1/`) pueden variar según los datos existentes
- **Credenciales de prueba**: 
  - **Email**: `admin@minierp.com`
  - **Password**: `test123456`
- **Verificar usuarios disponibles**: Si las credenciales no funcionan, verifica que los datos de prueba se hayan cargado
- **URLs corregidas**: Todas las URLs en los ejemplos están actualizadas para funcionar correctamente

### Verificar Usuarios Disponibles
```bash
# Listar usuarios (requiere autenticación de admin)
curl -X GET $BASE_URL/api/users/users/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq '.results[] | {id, username, email}'

# O crear un superusuario si no hay datos
python manage.py createsuperuser
```

## 📚 Endpoints Principales

### Usuarios y Autenticación
- `POST /api/users/register/` - Registro de usuario
- `POST /api/users/login/` - Login
- `GET /api/users/profile/` - Perfil del usuario
- `PUT /api/users/update_profile/` - Actualizar perfil
- `POST /api/users/change_password/` - Cambiar contraseña
- `POST /api/users/logout/` - Logout

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

## 👥 Usuarios de Prueba

El sistema incluye usuarios predefinidos:

| Usuario | Email | Contraseña | Rol |
|---------|-------|------------|-----|
| admin | admin@minierp.com | test123456 | Administrador |
| manager | manager@minierp.com | test123456 | Manager |
| sales | sales@minierp.com | test123456 | Ventas |

## 📊 Datos de Prueba

El sistema incluye datos de ejemplo:

### Productos
- Laptop Dell XPS 13
- iPhone 15 Pro
- Nike Air Max 270
- Python Programming Book
- Garden Hose 50ft
- Basketball

### Categorías
- Electronics
- Clothing
- Books
- Home & Garden
- Sports

### Clientes y Proveedores
- 5 clientes de ejemplo
- 5 proveedores de ejemplo

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=mini_erp
DB_USER=erp_user
DB_PASSWORD=erp_password
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRES=True
```

### Configuración de Base de Datos

El proyecto está configurado para usar **PostgreSQL** por defecto. Para usar SQLite:
```env
USE_POSTGRES=False
```

### Configuración de PostgreSQL

Si no tienes PostgreSQL instalado, puedes instalarlo:

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Descargar desde [postgresql.org](https://www.postgresql.org/download/windows/)

**Configuración automática:**
```bash
python manage_dev.py postgres
```

## 📖 Documentación de la API

La documentación completa está disponible en:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 🧪 Testing

### Tests Unitarios
```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos por módulo
python manage.py test users
python manage.py test inventory
python manage.py test sales
python manage.py test purchases
python manage.py test reports

# Tests con SQLite (para desarrollo)
USE_POSTGRES=False python manage.py test
```

### Tests End-to-End
```bash
# Ejecutar tests E2E
python manage.py test tests_e2e

# Tests E2E específicos
python manage.py test tests_e2e.test_authentication
```

### Tests con Docker
```bash
# Construir imagen
docker build -t mini-erp .

# Ejecutar tests en contenedor
docker run --rm mini-erp python manage.py test

# Tests con Docker Compose
docker compose build
docker compose up -d
docker compose exec web python manage.py test
docker compose down
```

### Cobertura de Tests
- **66 tests unitarios** cubriendo todos los modelos
- **10 tests E2E** probando endpoints de autenticación
- **Validación de datos** y lógica de negocio
- **Tests de integración** con base de datos

## 🔄 CI/CD

El proyecto incluye GitHub Actions workflows para automatizar testing:

### Workflows Disponibles
- **`.github/workflows/tests.yml`**: Tests unitarios y E2E con PostgreSQL
- **`.github/workflows/docker-compose.yml`**: Tests con Docker Compose

### Triggers
- Push a `main` y `develop`
- Pull Requests a `main` y `develop`

### Jobs
1. **Test**: Ejecuta tests unitarios y E2E con PostgreSQL
2. **Docker Test**: Construye y prueba la imagen Docker
3. **Docker Compose Test**: Prueba el stack completo con Docker Compose

## 🆘 Comandos Útiles

```bash
# Ver estado del proyecto
python scripts_utils/manage_dev.py status

# Configurar PostgreSQL
python scripts_utils/manage_dev.py postgres

# Ejecutar tests
python scripts_utils/manage_dev.py test

# Docker (opcional)
python scripts_utils/manage_dev.py docker-setup
python scripts_utils/manage_dev.py docker-stop

# Generar SECRET_KEY seguro
python scripts_utils/manage_dev.py secret-key
```

### Scripts de Gestión

El proyecto incluye scripts para facilitar el desarrollo:

```bash
# Configurar entorno completo
python scripts_utils/manage_dev.py setup

# Crear superusuario
python scripts_utils/manage_dev.py superuser

# Iniciar servidor
python scripts_utils/manage_dev.py run
```

### Generación de SECRET_KEYs

Para generar SECRET_KEYs seguros para producción:

```bash
# Script independiente con opciones avanzadas
python scripts_utils/generate_secret_key.py --django-format --env-file

# Comando integrado en manage_dev.py
python scripts_utils/manage_dev.py secret-key
```

**Opciones del script `generate_secret_key.py`:**
- `--length N`: Longitud del SECRET_KEY (default: 50)
- `--django-format`: Usar formato específico de Django
- `--env-file`: Generar formato para archivo .env
- `--settings-file`: Generar formato para settings.py

## 📁 Estructura del Proyecto

```
mini-erp/
├── mini_erp/          # Configuración principal
├── users/             # Gestión de usuarios y roles
├── inventory/         # Gestión de inventario
├── sales/            # Gestión de ventas
├── purchases/        # Gestión de compras
├── reports/          # Sistema de reportes
├── fixtures/         # Datos de prueba
├── tests_e2e/        # Tests end-to-end
├── scripts_utils/    # Scripts de utilidades
│   ├── manage_dev.py     # Script principal de gestión
│   ├── generate_secret_key.py # Generador de SECRET_KEYs
│   ├── backup_db.py      # Script de backup PostgreSQL
│   └── README.md         # Documentación de scripts
├── requirements.txt  # Dependencias
├── Dockerfile        # Configuración Docker
├── docker-compose.yml # Orquestación Docker
└── README.md         # Documentación principal
```

## 🎯 Casos de Uso para Estudiantes

### Frontend Development
1. **Dashboard**: Crear un dashboard con estadísticas principales
2. **CRUD Operations**: Implementar operaciones CRUD para cada módulo
3. **Authentication**: Integrar sistema de login/logout
4. **Real-time Updates**: Implementar actualizaciones en tiempo real
5. **Reports**: Crear visualizaciones de reportes
6. **Responsive Design**: Diseño responsive para móviles

### Tecnologías Frontend Sugeridas
- **React** con TypeScript
- **Vue.js** con Composition API
- **Angular** con RxJS
- **Svelte** con SvelteKit
- **Next.js** para SSR

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

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Email: admin@minierp.com
- Documentación: http://localhost:8000/api/docs/

## 🔄 Actualizaciones

Para actualizar el proyecto:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```

---

## 📝 Notas de la Documentación

- **Inicio Rápido**: La sección "⚡ Inicio Rápido" te permite comenzar en 5 minutos
- **Scripts de Utilidades**: Todos los scripts están organizados en `scripts_utils/` con su propia documentación
- **Tests**: Incluye tests unitarios para modelos y tests end-to-end para endpoints
- **Seguridad**: Genera SECRET_KEYs únicos para cada entorno

**¡Disfruta desarrollando tu frontend con este Mini ERP! 🚀**
