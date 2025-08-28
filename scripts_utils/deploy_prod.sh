#!/bin/bash

# Script de deploy para producción
set -e

echo "🚀 Iniciando deploy de producción..."
echo "=================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar que existe el archivo .env.prod
if [ ! -f ".env.prod" ]; then
    echo "⚠️  No se encontró el archivo .env.prod"
    echo "🔧 Generando archivo .env.prod con valores seguros..."
    
    # Ejecutar el script de configuración
    python3 scripts_utils/setup_prod_env.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al generar .env.prod"
        exit 1
    fi
fi

# Cargar variables de entorno
echo "📋 Cargando variables de entorno..."
source .env.prod

# Verificar que las variables necesarias están definidas
required_vars=("DATABASE_URL" "SECRET_KEY" "DB_PASSWORD" "DEBUG" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Variable $var no está definida en .env.prod"
        exit 1
    fi
done

echo "✅ Variables de entorno cargadas correctamente"

# Detener contenedores existentes si están corriendo
echo "🛑 Deteniendo contenedores existentes..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Construir y levantar contenedores
echo "🔨 Levantando contenedores de producción..."
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 10

# Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Cargar datos iniciales si es necesario
echo "📦 Cargando datos iniciales..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py loaddata fixtures/*.json || true

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo ""
echo "🎉 ¡Deploy completado exitosamente!"
echo ""
echo "📋 Información del deploy:"
echo "   - URL: http://localhost:8800"
echo "   - Base de datos: PostgreSQL en puerto 5432"
echo "   - Contenedores: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - Detener: docker-compose -f docker-compose.prod.yml down"
echo "   - Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Actualiza ALLOWED_HOSTS y CORS_ALLOWED_ORIGINS en .env.prod con tu dominio real"
echo "   - Configura un proxy reverso (nginx) para producción"
echo "   - Configura SSL/TLS para HTTPS"
