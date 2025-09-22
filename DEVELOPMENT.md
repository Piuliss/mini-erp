# Mini ERP - Guía de Desarrollo

Esta guía contiene toda la información técnica detallada para desarrolladores, incluyendo instalación completa, configuración, troubleshooting y detalles de implementación.

## 🚀 Instalación Completa

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd mini-erp
```

2. **Crear archivo de configuración**
```bash
# Crear archivo .env para desarrollo
cp env.example .env
```

3. **Ejecutar con Docker Compose**
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

## 📊 Datos de Prueba

El sistema incluye datos de ejemplo con **fixtures corregidos** que funcionan correctamente:

### Usuarios (con contraseñas funcionales)
- **admin@minierp.com** / test123456 (Administrador)
- **manager@minierp.com** / test123456 (Manager)
- **sales@minierp.com** / test123456 (Ventas)

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

### Fixtures

Los fixtures incluyen datos de prueba. Si hay problemas con las contraseñas:

```bash
# Cargar fixtures
docker exec mini-erp-web-1 python manage.py loaddata fixtures/*.json

# Si las contraseñas no funcionan, resetearlas:
docker exec -it mini-erp-web-1 python manage.py shell -c "
from users.models import User
for user in User.objects.all():
    user.set_password('test123456')
    user.save()
    print(f'Contraseña actualizada para {user.email}')
"
```

## 🔧 Configuración

### Variables de Entorno

El proyecto usa variables de entorno para configuración flexible. El archivo `docker-compose.yml` está configurado para leer automáticamente las variables del archivo `.env`.

**Crear archivo `.env`**:
```bash
# Copiar el archivo de ejemplo
cp env.example .env
```

**Contenido del archivo `.env`**:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Settings
DB_NAME=mini_erp
DB_USER=erp_user
DB_PASSWORD=erp_password
DB_HOST=db
DB_PORT=5432
USE_POSTGRES=True

# JWT Settings (opcional)
# ACCESS_TOKEN_LIFETIME=1:00:00
# REFRESH_TOKEN_LIFETIME=1:00:00

# CORS Settings (opcional)
# CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Ventajas de usar `.env`**:
- ✅ Configuración centralizada
- ✅ Valores por defecto seguros
- ✅ Fácil personalización
- ✅ No hardcodeado en archivos
- ✅ Diferentes configuraciones por entorno

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

# Generar SECRET_KEY seguro (si es necesario)
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
# Comando integrado en manage_dev.py
python scripts_utils/manage_dev.py secret-key

# O usar herramientas online como:
# https://djecrety.ir/
```

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
│   └── README.md         # Documentación de scripts
├── requirements.txt  # Dependencias
├── Dockerfile        # Configuración Docker
├── docker-compose.yml # Orquestación Docker
└── README.md         # Documentación principal
```

## 🐳 Gestión de Docker en Producción

### Verificar Estado del Servidor
```bash
# Verificar contenedores en ejecución
docker container ls -a

# Ver logs del contenedor web
docker logs mini-erp-web-1

# Ver logs en tiempo real
docker logs -f mini-erp-web-1

# Verificar estado de la base de datos
docker exec mini-erp-db-1 pg_isready -U minierp_user -d minierp_prod
```

### Comandos de Gestión en Producción
```bash
# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Reconstruir y reiniciar
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar variables de entorno
docker exec mini-erp-web-1 env | grep -E "(DEBUG|ALLOWED_HOSTS|SECRET_KEY)"

# Ejecutar comandos de Django en el contenedor
docker exec mini-erp-web-1 python manage.py check
docker exec mini-erp-web-1 python manage.py showmigrations

# Verificar base de datos
docker exec mini-erp-web-1 python manage.py dbshell

# Verificar y cargar datos de prueba
docker exec mini-erp-web-1 python manage.py loaddata fixtures/*.json

# Crear superusuario si no existe
docker exec -it mini-erp-web-1 python manage.py createsuperuser

# Verificar usuarios existentes
docker exec mini-erp-web-1 python manage.py shell -c "
from users.models import User
print('Usuarios existentes:')
for user in User.objects.all():
    print(f'- {user.email} ({user.username})')
"
```

### Backup y Restauración
```bash
# Backup de la base de datos
docker exec mini-erp-db-1 pg_dump -U minierp_user minierp_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker exec -i mini-erp-db-1 psql -U minierp_user minierp_prod < backup_file.sql

# Backup de archivos de configuración
cp .env.prod .env.prod.backup.$(date +%Y%m%d_%H%M%S)
```

### Comandos de Emergencia
```bash
# Reiniciar todo el stack
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs en tiempo real
docker logs -f mini-erp-web-1

# Acceder al shell de Django
docker exec -it mini-erp-web-1 python manage.py shell

# Verificar configuración
docker exec mini-erp-web-1 python manage.py check
```

## 🔧 Solución de Problemas

### Problemas Comunes en Producción

#### 1. Endpoints no responden (404)
**Síntomas**: Los endpoints devuelven 404 Not Found
**Solución**: Verificar que las URLs sean correctas:
- ✅ Correcto: `/api/users/users/login/`
- ❌ Incorrecto: `/api/users/login/`

#### 2. Error de autenticación (400)
**Síntomas**: Login devuelve "Invalid credentials"
**Solución rápida**:
```bash
# Resetear contraseñas de todos los usuarios
docker exec -it mini-erp-web-1 python manage.py shell -c "
from users.models import User
for user in User.objects.all():
    user.set_password('test123456')
    user.save()
    print(f'Contraseña actualizada para {user.email}')
"
```

#### 3. Error de conectividad
**Síntomas**: No se puede conectar al servidor
**Solución**:
```bash
# Verificar contenedores
docker container ls -a

# Verificar logs
docker logs mini-erp-web-1

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart
```

#### 4. Error de permisos (401)
**Síntomas**: Endpoints devuelven 401 Unauthorized
**Causa**: Endpoints requieren autenticación
**Solución**: Incluir token JWT en el header:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" $PROD_URL/api/inventory/products/
```

### Solución Rápida de Problemas

#### Si las credenciales no funcionan:
```bash
# Acceder a la consola de Django en producción
docker exec -it mini-erp-web-1 python manage.py shell

# En la consola, ejecutar:
from users.models import User
for user in User.objects.all():
    user.set_password('test123456')
    user.save()
    print(f'Contraseña actualizada para {user.email}')
```


## 🚀 Despliegue en Producción

### Docker Hub y GitHub Actions

Para desplegar en producción usando Docker Hub, sigue estos pasos:

#### 1. Configurar GitHub Actions para Docker Hub

Crea el archivo `.github/workflows/docker-publish.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: docker.io
  IMAGE_NAME: honeyjack/mini-erp

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### 2. Configurar Secrets en GitHub

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions y agrega:

- `DOCKER_USERNAME`: Tu usuario de Docker Hub (honeyjack)
- `DOCKER_PASSWORD`: Tu token de acceso de Docker Hub

#### 3. Comandos de Producción

```bash
# Desplegar en producción usando la imagen de Docker Hub
docker run -d \
  --name mini-erp-prod \
  -p 80:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-production-secret-key \
  -e DEBUG=False \
  honeyjack/mini-erp:latest

# Usar Docker Compose en producción
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs
docker logs mini-erp-prod

# Escalar la aplicación
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

#### 4. Docker Compose para Producción

El archivo `docker-compose.prod.yml` ya está configurado en el proyecto:

```yaml
version: '3.8'

services:
  web:
    image: honeyjack/mini-erp:latest
    ports:
      - "8800:8000"
    env_file:
      - .env.prod
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    env_file:
      - .env.prod
    environment:
      - POSTGRES_DB=minierp_prod
      - POSTGRES_USER=minierp_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 5. Configuración de Variables de Entorno para Producción

Crea un archivo `.env.prod` basado en `env.prod.example`:

```bash
# Base de datos - Variables individuales (simple)
DB_PASSWORD=your_secure_password
POSTGRES_PASSWORD=your_secure_password
DB_NAME=minierp_prod
POSTGRES_DB=minierp_prod
DB_USER=minierp_user
POSTGRES_USER=minierp_user
DB_HOST=db
DB_PORT=5432
USE_POSTGRES=True

# Django
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 6. Comandos de Despliegue

```bash
# Desplegar en producción
./scripts_utils/deploy_prod.sh

# Verificar el estado
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Detener servicios
docker-compose -f docker-compose.prod.yml down
```

### Monitoreo y Logs

```bash
# Ver logs en tiempo real
docker logs -f mini-erp-prod

# Ver logs de los últimos 100 líneas
docker logs --tail 100 mini-erp-prod

# Ver estadísticas del contenedor
docker stats mini-erp-prod

# Backup de la base de datos
docker exec mini-erp-db pg_dump -U minierp_user minierp_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 🔄 Actualizaciones

Para actualizar el proyecto:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```

## 📝 Notas de la Documentación

- **Inicio Rápido**: La sección "⚡ Inicio Rápido" te permite comenzar en 5 minutos
- **Scripts de Utilidades**: Todos los scripts están organizados en `scripts_utils/` con su propia documentación
- **Tests**: Incluye tests unitarios para modelos y tests end-to-end para endpoints
- **Seguridad**: Genera SECRET_KEYs únicos para cada entorno

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

---

**Esta guía está diseñada para desarrolladores que necesitan información técnica detallada sobre el proyecto.**
