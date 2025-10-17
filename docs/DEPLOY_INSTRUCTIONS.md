# Instrucciones de Despliegue - Corrección de Swagger/ReDoc en Producción

## Problema Resuelto
Las URLs de Swagger UI y ReDoc no funcionaban en producción debido a que Django no servía archivos estáticos cuando `DEBUG=False`.

## Solución Implementada
Se agregó **WhiteNoise** para servir archivos estáticos eficientemente en producción.

## Cambios Realizados

### 1. Dependencias Actualizadas
- Se agregó `whitenoise==6.6.0` a `requirements.txt`

### 2. Configuración de Django
- Se agregó WhiteNoise a `INSTALLED_APPS` en `settings.py`
- Se agregó WhiteNoise middleware en `MIDDLEWARE`
- Se configuró `STORAGES` para usar `CompressedManifestStaticFilesStorage`

### 3. Dockerfile
- Se agregó `curl` para los health checks
- Se agregó `collectstatic` al comando de inicio

## Pasos para Desplegar

### Opción 1: Usando el Script de Despliegue (Recomendado)

```bash
cd /ruta/al/proyecto
chmod +x scripts_utils/deploy_prod.sh
./scripts_utils/deploy_prod.sh
```

El script automáticamente:
1. Descarga la última imagen de Docker Hub
2. Recrea el contenedor web
3. Ejecuta migraciones
4. Recolecta archivos estáticos
5. Verifica el estado de la aplicación

### Opción 2: Despliegue Manual

```bash
# 1. Construir nueva imagen (si estás en el servidor de producción)
docker compose -f docker-compose.prod.yml build

# 2. Detener servicios
docker compose -f docker-compose.prod.yml down

# 3. Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# 4. Recolectar archivos estáticos (ya se hace automáticamente en el CMD del Dockerfile)
# docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 5. Verificar estado
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
```

### Opción 3: Desde Docker Hub

Si estás desplegando desde Docker Hub (imagen pre-construida):

```bash
# 1. Pull de la nueva imagen
docker compose -f docker-compose.prod.yml pull

# 2. Recrear contenedores
docker compose -f docker-compose.prod.yml up -d --force-recreate

# 3. Verificar logs
docker compose -f docker-compose.prod.yml logs -f web
```

## Verificación

Después del despliegue, verifica que las siguientes URLs funcionen:

- **Swagger UI**: http://185.218.124.154:8800/api/docs/
- **ReDoc**: http://185.218.124.154:8800/api/redoc/
- **Admin**: http://185.218.124.154:8800/admin/

## Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f web

# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml ps

# Ejecutar collectstatic manualmente (si es necesario)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Reiniciar solo el contenedor web
docker compose -f docker-compose.prod.yml restart web

# Ver archivos estáticos recolectados
docker compose -f docker-compose.prod.yml exec web ls -la staticfiles/

# Acceder al shell de Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

## Notas Importantes

1. **WhiteNoise** comprime y cachea archivos estáticos automáticamente para mejor rendimiento
2. Los archivos estáticos se recolectan automáticamente al iniciar el contenedor
3. No es necesario configurar un servidor web adicional (Nginx/Apache) para servir estáticos
4. Los cambios son compatibles tanto con producción como con desarrollo

## Troubleshooting

### Si las URLs siguen sin funcionar:

1. Verifica que el contenedor esté corriendo:
```bash
docker compose -f docker-compose.prod.yml ps
```

2. Verifica que `collectstatic` se ejecutó correctamente:
```bash
docker compose -f docker-compose.prod.yml logs web | grep collectstatic
```

3. Verifica que los archivos estáticos existen:
```bash
docker compose -f docker-compose.prod.yml exec web ls -la staticfiles/
```

4. Verifica la configuración de DEBUG:
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; print(f'DEBUG={settings.DEBUG}')"
```

5. Reinicia el contenedor:
```bash
docker compose -f docker-compose.prod.yml restart web
```

### Si hay errores de "manifest file not found":

Esto puede ocurrir si `collectstatic` no se ejecutó correctamente. Ejecuta manualmente:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml restart web
```

## Información de Contacto

Para soporte adicional, revisa los logs completos:
```bash
docker compose -f docker-compose.prod.yml logs --tail=100 web
```

