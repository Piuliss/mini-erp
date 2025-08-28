# 🚀 Guía de Deploy en Producción

## 📋 Configuración del Servidor

### 1. Crear usuario deploy (sin sudo)

```bash
# Conectarse al servidor como root
ssh root@185.218.124.154

# Crear usuario deploy sin sudo
sudo adduser deploy

# Crear directorio para el proyecto
sudo mkdir -p /home/deploy/mini-erp
sudo chown deploy:deploy /home/deploy/mini-erp

# Agregar usuario al grupo docker (necesario para usar Docker)
sudo usermod -aG docker deploy

# Cambiar al usuario deploy
su - deploy
```

### 2. Configurar SSH Key para deploy

```bash
# En tu máquina local, generar SSH key si no tienes una
ssh-keygen -t rsa -b 4096 -C "deploy@185.218.124.154"

# Copiar la clave pública al servidor
ssh-copy-id deploy@185.218.124.154
```

### 3. Instalar Docker y Docker Compose

```bash
# Conectarse como deploy
ssh deploy@185.218.124.154

# Instalar Docker (como root primero)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose (como root)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario deploy al grupo docker
sudo usermod -aG docker deploy

# Reiniciar sesión para aplicar cambios
exit
ssh deploy@185.218.124.154
```

### 4. Clonar el repositorio

```bash
# Clonar el proyecto en el directorio creado
cd /home/deploy/mini-erp
git clone https://github.com/tu-usuario/mini-erp.git .
# Nota: el punto al final clona dentro del directorio actual

# Crear archivo de configuración de producción
cp env.prod.example .env
```

### 5. Configurar variables de entorno

```bash
# Editar el archivo .env
nano .env
```

Configurar con valores reales:

```bash
# Base de datos
DATABASE_URL=postgresql://minierp_user:TU_PASSWORD_SEGURO@db:5432/minierp_prod
DB_PASSWORD=TU_PASSWORD_SEGURO

# Django
SECRET_KEY=TU_SECRET_KEY_MUY_SEGURO_AQUI
DEBUG=False
ALLOWED_HOSTS=185.218.124.154,localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://185.218.124.154:8800,https://185.218.124.154:8800
```

### 6. Generar SECRET_KEY

```bash
# Generar una SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🔧 Configuración de GitHub Actions

### 1. Configurar secrets en GitHub

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions

Agregar los siguientes secrets:

- `DEPLOY_SSH_KEY`: Tu clave SSH privada para conectar al servidor
- `SERVER_IP`: IP del servidor de producción (185.218.124.154)
- `DOCKER_USERNAME`: Tu usuario de Docker Hub
- `DOCKER_PASSWORD`: Tu contraseña de Docker Hub

### 2. Configurar environment en GitHub

Crear un environment llamado `production` en:
Settings → Environments → New environment

## 🚀 Deploy Automático

### Opción 1: Deploy automático con GitHub Actions

El deploy se ejecutará automáticamente cuando:
1. Se haga push a la rama `main`
2. Los tests pasen exitosamente
3. Se construya la imagen de Docker

### Opción 2: Deploy manual

```bash
# Desde tu máquina local
./scripts_utils/deploy.sh 185.218.124.154 deploy
```

### Opción 3: Deploy directo en el servidor

```bash
# Conectarse al servidor
ssh deploy@185.218.124.154

# Navegar al proyecto
cd mini-erp

# Hacer deploy
git pull origin main
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate
docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
```

## 🔍 Verificación del Deploy

### 1. Verificar contenedores

```bash
docker compose -f docker-compose.prod.yml ps
```

### 2. Verificar logs

```bash
# Logs de la aplicación
docker compose -f docker-compose.prod.yml logs web

# Logs de la base de datos
docker compose -f docker-compose.prod.yml logs db
```

### 3. Verificar acceso

```bash
# Probar la API
curl http://185.218.124.154:8800/api/

# Verificar estado de salud
curl http://185.218.124.154:8800/health/
```

## 🛠️ Comandos útiles

### Reiniciar servicios

```bash
docker compose -f docker-compose.prod.yml restart
```

### Ver logs en tiempo real

```bash
docker compose -f docker-compose.prod.yml logs -f web
```

### Acceder al contenedor

```bash
docker compose -f docker-compose.prod.yml exec web bash
```

### Backup de base de datos

```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U minierp_user mini_erp_prod > backup.sql
```

## 🔒 Seguridad

### 1. Usuario deploy sin privilegios

El usuario `deploy` está configurado sin acceso sudo, lo que es más seguro:
- Solo puede ejecutar comandos Docker
- No puede modificar archivos del sistema
- Solo tiene acceso a su directorio home

### 2. Firewall

```bash
# Configurar firewall (como root)
sudo ufw allow 22/tcp
sudo ufw allow 8800/tcp
sudo ufw enable
```

### 3. Configurar sudoers (opcional, solo si necesitas sudo)

Si en algún momento necesitas que el usuario deploy ejecute algún comando con sudo:

```bash
# Como root, editar sudoers
sudo visudo

# Agregar línea específica (ejemplo para reiniciar Docker)
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart docker
```

### 4. SSL/HTTPS (Opcional)

Para producción real, considera usar un proxy reverso con Nginx y Let's Encrypt para SSL.

## 📞 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs web

# Verificar variables de entorno
docker compose -f docker-compose.prod.yml config
```

### Problema: Base de datos no conecta

```bash
# Verificar estado de PostgreSQL
docker compose -f docker-compose.prod.yml exec db pg_isready -U minierp_user

# Verificar logs de DB
docker compose -f docker-compose.prod.yml logs db
```

### Problema: Migraciones fallan

```bash
# Ejecutar migraciones manualmente
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --verbosity=2
```

## 🌐 URLs de la aplicación

- **API Principal**: http://185.218.124.154:8800/api/
- **Admin Django**: http://185.218.124.154:8800/admin/
- **Documentación API**: http://185.218.124.154:8800/api/docs/

---

**¡Listo! Tu aplicación estará disponible en http://185.218.124.154:8800**
