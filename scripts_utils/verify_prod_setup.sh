#!/bin/bash

# Script para verificar la configuración del entorno de producción
set -e

echo "🔍 Verificando configuración del entorno de producción..."
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar que Docker está instalado y funcionando
echo "🐳 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está ejecutándose o no tienes permisos"
    exit 1
fi

echo "✅ Docker está funcionando correctamente"

# Verificar que Docker Compose está disponible
echo "📦 Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker Compose está disponible"

# Verificar archivos necesarios
echo "📁 Verificando archivos necesarios..."

required_files=(
    "docker-compose.prod.yml"
    "env.prod.example"
    "scripts_utils/deploy_prod.sh"
    "scripts_utils/setup_prod_env.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Error: No se encontró el archivo $file"
        exit 1
    fi
    echo "✅ $file encontrado"
done

# Verificar que los scripts son ejecutables
echo "🔧 Verificando permisos de scripts..."
chmod +x scripts_utils/deploy_prod.sh
chmod +x scripts_utils/setup_prod_env.py

echo "✅ Scripts configurados correctamente"

# Verificar archivo .env.prod
if [ -f ".env.prod" ]; then
    echo "✅ Archivo .env.prod encontrado"
    
    # Verificar variables críticas
    echo "🔍 Verificando variables de entorno críticas..."
    
    # Función para verificar variable
    check_var() {
        local var_name=$1
        local var_line=$(grep "^${var_name}=" .env.prod | head -1)
        
        if [ -z "$var_line" ]; then
            echo "❌ Error: Variable $var_name no está definida en .env.prod"
            return 1
        fi
        
        local var_value="${var_line#*=}"
        var_value=$(echo "$var_value" | tr -d '\r' | tr -d '"' | tr -d "'")
        
        if [ -z "$var_value" ]; then
            echo "❌ Error: Variable $var_name está vacía"
            return 1
        elif [ "$var_value" = "your_secure_password" ] || [ "$var_value" = "your-production-secret-key-here" ]; then
            echo "❌ Error: Variable $var_name tiene valor por defecto"
            return 1
        else
            echo "✅ $var_name configurada correctamente"
            return 0
        fi
    }
    
    # Verificar variables críticas (sin cargar el archivo como script)
    echo "🔍 Verificando variables críticas..."
    check_var "DB_PASSWORD" || exit 1
    check_var "SECRET_KEY" || exit 1
    check_var "DATABASE_URL" || exit 1
    check_var "DEBUG" || exit 1
    check_var "ALLOWED_HOSTS" || exit 1
    
else
    echo "⚠️  Archivo .env.prod no encontrado"
    echo "💡 Ejecuta: python scripts_utils/setup_prod_env.py"
    exit 1
fi

# Verificar conectividad de red
echo "🌐 Verificando conectividad de red..."
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    echo "⚠️  Advertencia: No se pudo verificar conectividad a internet"
else
    echo "✅ Conectividad de red OK"
fi

# Verificar puertos disponibles
echo "🔌 Verificando puertos disponibles..."
if netstat -tuln | grep ":8800 " &> /dev/null; then
    echo "⚠️  Advertencia: Puerto 8800 ya está en uso"
else
    echo "✅ Puerto 8800 disponible"
fi

if netstat -tuln | grep ":5432 " &> /dev/null; then
    echo "⚠️  Advertencia: Puerto 5432 ya está en uso"
else
    echo "✅ Puerto 5432 disponible"
fi

echo ""
echo "🎉 Verificación completada exitosamente!"
echo ""
echo "📋 Resumen:"
echo "   ✅ Docker y Docker Compose funcionando"
echo "   ✅ Archivos necesarios presentes"
echo "   ✅ Scripts ejecutables"
echo "   ✅ Variables de entorno configuradas"
echo ""
echo "🚀 El entorno está listo para deploy"
echo "   Ejecuta: ./scripts_utils/deploy_prod.sh"
