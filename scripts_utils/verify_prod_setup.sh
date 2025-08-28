#!/bin/bash

# Script para verificar la configuración de producción
set -e

echo "🔍 Verificando configuración de producción..."
echo "============================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar que existe el archivo .env.prod
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: No se encontró el archivo .env.prod"
    echo "🔧 Ejecuta: python3 scripts_utils/setup_prod_env.py"
    exit 1
fi

# Cargar variables de entorno
echo "📋 Cargando variables de entorno..."
export $(grep -v '^#' .env.prod | xargs)

# Verificar variables críticas
echo "🔍 Verificando variables críticas..."

# Función para verificar variable
check_var() {
    local var_name=$1
    local var_value="${!var_name}"
    
    if [ -n "$var_value" ] && [ "$var_value" != "your_secure_password" ] && [ "$var_value" != "your-production-secret-key-here" ]; then
        echo "✅ $var_name: configurada"
        return 0
    else
        echo "❌ $var_name: no configurada o valor por defecto"
        return 1
    fi
}

# Verificar variables requeridas
# Priorizar DATABASE_URL si está disponible
if [ -n "$DATABASE_URL" ]; then
    echo "✅ DATABASE_URL: configurada"
    required_vars=("SECRET_KEY")
else
    echo "⚠️  DATABASE_URL: no configurada, verificando variables individuales..."
    required_vars=("DB_PASSWORD" "SECRET_KEY" "DB_NAME" "DB_USER" "DB_HOST" "DB_PORT" "USE_POSTGRES")
fi

all_good=true

for var in "${required_vars[@]}"; do
    if ! check_var "$var"; then
        all_good=false
    fi
done

if [ "$all_good" = false ]; then
    echo ""
    echo "❌ Error: Algunas variables no están configuradas correctamente"
    echo "🔧 Ejecuta: python3 scripts_utils/setup_prod_env.py"
    exit 1
fi

# Verificar que Docker está disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está ejecutándose o no tienes permisos"
    exit 1
fi

echo "✅ Docker está funcionando correctamente"

# Verificar que docker compose está disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Error: docker no está instalado"
    exit 1
fi

# Verificar que docker compose funciona
if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker compose no está disponible"
    exit 1
fi

echo "✅ docker compose está disponible"

# Verificar que el archivo docker-compose.prod.yml existe
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: No se encontró docker-compose.prod.yml"
    exit 1
fi

echo "✅ docker-compose.prod.yml encontrado"

# Verificar que la imagen existe (opcional)
echo "🔍 Verificando imagen Docker..."
if docker images | grep -q "honeyjack/mini-erp"; then
    echo "✅ Imagen honeyjack/mini-erp encontrada"
else
    echo "⚠️  Imagen honeyjack/mini-erp no encontrada localmente"
    echo "   Se descargará automáticamente durante el deploy"
fi

echo ""
echo "🎉 ¡Configuración verificada correctamente!"
echo ""
echo "📋 Resumen:"
echo "   - Variables de entorno: ✅"
echo "   - Docker: ✅"
echo "   - docker-compose: ✅"
echo "   - Archivos de configuración: ✅"
echo ""
echo "🚀 Listo para ejecutar: ./scripts_utils/deploy_prod.sh"
