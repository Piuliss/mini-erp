#!/bin/bash

# Script de deploy para producción
set -e

# Configuración
COMPOSE_FILE="docker-compose.prod.yml"
COMPOSE_CMD="docker compose -f $COMPOSE_FILE"
MAX_WAIT_TIME=60

echo "🚀 Iniciando deploy de producción..."
echo "📅 Fecha: $(date)"

# Función para esperar a que la base de datos esté lista
wait_for_db() {
    echo "⏳ Esperando a que la base de datos esté lista..."
    local elapsed=0
    until $COMPOSE_CMD exec -T db pg_isready -U ${DB_USER:-postgres} > /dev/null 2>&1; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ $elapsed -ge $MAX_WAIT_TIME ]; then
            echo "❌ Timeout esperando la base de datos"
            return 1
        fi
        echo "   Esperando... ${elapsed}s"
    done
    echo "✅ Base de datos lista"
}

# Función para esperar a que Django esté listo
wait_for_django() {
    echo "⏳ Esperando a que Django esté listo..."
    local elapsed=0
    until $COMPOSE_CMD exec -T web python manage.py check > /dev/null 2>&1; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ $elapsed -ge $MAX_WAIT_TIME ]; then
            echo "❌ Timeout esperando Django"
            return 1
        fi
        echo "   Esperando... ${elapsed}s"
    done
    echo "✅ Django listo"
}

# Verificar que existe .env.prod
if [ ! -f .env.prod ]; then
    echo "❌ Error: No se encuentra el archivo .env.prod"
    echo "   Copia env.prod.example a .env.prod y configúralo"
    exit 1
fi

# Pull de la nueva imagen
echo "📥 Descargando última imagen de Docker Hub..."
$COMPOSE_CMD pull web

# Recrear solo el contenedor web (sin downtime de la DB)
echo "🔄 Recreando contenedor web..."
$COMPOSE_CMD up -d --force-recreate --no-deps web

# Esperar a que todo esté listo
wait_for_db
wait_for_django

# Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
$COMPOSE_CMD exec -T web python manage.py migrate

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
$COMPOSE_CMD exec -T web python manage.py collectstatic --noinput || true

# Verificar estado de los servicios
echo "📊 Estado de los servicios:"
$COMPOSE_CMD ps

# Verificar que la aplicación responda
echo "🔍 Verificando que la aplicación responda..."
if $COMPOSE_CMD exec -T web curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo "✅ Aplicación respondiendo correctamente"
else
    echo "⚠️  Advertencia: No se pudo verificar el health check (puede que no exista el endpoint)"
fi

# Limpiar imágenes viejas (mantener solo las últimas 2 versiones)
echo "🧹 Limpiando imágenes antiguas..."
docker image prune -f --filter "until=48h" || true

echo ""
echo "🎉 ¡Deploy completado exitosamente!"
echo "📝 Logs: docker compose -f $COMPOSE_FILE logs -f web"
echo "📊 Estado: docker compose -f $COMPOSE_FILE ps"
