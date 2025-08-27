# Scripts de Utilidades - Mini ERP

Esta carpeta contiene scripts de utilidades para facilitar el desarrollo y gestión del proyecto Mini ERP.

## 📁 Scripts Disponibles

### 🚀 manage_dev.py
Script principal de gestión del proyecto que automatiza tareas comunes de desarrollo.

**Comandos disponibles:**
```bash
# Configurar entorno completo
python scripts_utils/manage_dev.py setup

# Crear superusuario
python scripts_utils/manage_dev.py superuser

# Ejecutar tests
python scripts_utils/manage_dev.py test

# Iniciar servidor
python scripts_utils/manage_dev.py run

# Configurar con Docker
python scripts_utils/manage_dev.py docker-setup

# Detener Docker
python scripts_utils/manage_dev.py docker-stop

# Ver estado del proyecto
python scripts_utils/manage_dev.py status

# Configurar PostgreSQL
python scripts_utils/manage_dev.py postgres

# Generar SECRET_KEY seguro
python scripts_utils/manage_dev.py secret-key
```

### 🔐 generate_secret_key.py
Generador de SECRET_KEYs seguros para Django.

**Uso:**
```bash
# Generar SECRET_KEY básico
python scripts_utils/generate_secret_key.py

# Con formato específico de Django
python scripts_utils/generate_secret_key.py --django-format

# Para archivo .env
python scripts_utils/generate_secret_key.py --env-file

# Para settings.py
python scripts_utils/generate_secret_key.py --settings-file

# Con longitud personalizada
python scripts_utils/generate_secret_key.py --length 60
```

**Opciones:**
- `--length N`: Longitud del SECRET_KEY (default: 50)
- `--django-format`: Usar formato específico de Django
- `--env-file`: Generar formato para archivo .env
- `--settings-file`: Generar formato para settings.py

### 💾 backup_db.py
Script para backup y restore de la base de datos PostgreSQL.

**Uso:**
```bash
# Crear backup
python scripts_utils/backup_db.py create

# Listar backups disponibles
python scripts_utils/backup_db.py list

# Restaurar backup específico
python scripts_utils/backup_db.py restore backup_file.sql
```

## 🔧 Configuración

Todos los scripts están diseñados para ejecutarse desde la raíz del proyecto:

```bash
cd /path/to/mini-erp
python scripts_utils/manage_dev.py setup
```

## 📝 Notas Importantes

- Los scripts asumen que estás en la raíz del proyecto Mini ERP
- Para producción, siempre usa SECRET_KEYs únicos y seguros
- Los backups se guardan en la carpeta `backups/` (se crea automáticamente)
- Los scripts incluyen validaciones y manejo de errores

## 🆘 Solución de Problemas

Si encuentras problemas con los scripts:

1. Verifica que estés en la raíz del proyecto
2. Asegúrate de que las dependencias estén instaladas
3. Para PostgreSQL, verifica que el servicio esté ejecutándose
4. Revisa los permisos de los archivos (deben ser ejecutables)

## 🔄 Actualizaciones

Los scripts se actualizan junto con el proyecto. Para obtener la última versión:

```bash
git pull origin main
```
