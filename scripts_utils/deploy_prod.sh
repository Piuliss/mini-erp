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

# Verificar que existe el archivo .env.prod
if [ ! -f ".env.prod" ]; then
    echo "⚠️  No se encontró el archivo .env.prod"
    echo "🔧 Generando archivo .env.prod con valores seguros..."
    
    # Verificar que el script de configuración existe
    if [ ! -f "scripts_utils/setup_prod_env.py" ]; then
        echo "❌ Error: No se encontró scripts_utils/setup_prod_env.py"
        exit 1
    fi
    
    # Ejecutar el script de configuración
    python3 scripts_utils/setup_prod_env.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al generar .env.prod"
        exit 1
    fi
    
    # Verificar que se creó correctamente
    if [ ! -f ".env.prod" ]; then
        echo "❌ Error: No se pudo crear el archivo .env.prod"
        exit 1
    fi
    
    echo "✅ Archivo .env.prod generado exitosamente"
fi

# Verificar que el archivo .env.prod existe y tiene las variables necesarias
echo "📋 Verificando archivo .env.prod..."

# Función para verificar variable en el archivo .env.prod
check_env_var() {
    local var_name=$1
    if grep -q "^${var_name}=" .env.prod; then
        local var_value=$(grep "^${var_name}=" .env.prod | head -1 | cut -d'=' -f2- | tr -d '\r' | tr -d '"' | tr -d "'")
        if [ -n "$var_value" ] && [ "$var_value" != "your_secure_password" ] && [ "$var_value" != "your-production-secret-key-here" ]; then
            echo "✅ $var_name configurada correctamente"
            return 0
        else
            echo "❌ Error: Variable $var_name tiene valor por defecto o está vacía"
            return 1
        fi
    else
        echo "❌ Error: Variable $var_name no está definida en .env.prod"
        return 1
    fi
}

# Verificar variables críticas
required_vars=("DATABASE_URL" "SECRET_KEY" "DB_PASSWORD" "DEBUG" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    check_env_var "$var" || exit 1
done

echo "✅ Archivo .env.prod verificado correctamente"

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
