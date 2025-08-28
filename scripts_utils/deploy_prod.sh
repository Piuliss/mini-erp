#!/bin/bash

# Script de deploy para producción - Versión ultra simplificada
set -e

echo "🚀 Iniciando deploy de producción..."

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker compose -f docker-compose.prod.yml down --remove-orphans || true

# Levantar contenedores
echo "🔨 Levantando contenedores..."
docker compose -f docker-compose.prod.yml up -d

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 15

# Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Cargar datos iniciales
echo "📦 Cargando datos iniciales..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py loaddata fixtures/*.json || true

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo "🎉 ¡Deploy completado!"
