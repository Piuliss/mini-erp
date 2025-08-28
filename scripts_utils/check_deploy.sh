#!/bin/bash

# Script para verificar el estado del deploy
set -e

echo "🔍 Verificando estado del deploy..."
echo "=================================="

# Verificar contenedores
echo "🐳 Verificando contenedores..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Contenedores están ejecutándose"
else
    echo "❌ Contenedores no están ejecutándose"
    docker-compose -f docker-compose.prod.yml ps
    exit 1
fi

# Verificar conectividad de la aplicación
echo "🌐 Verificando conectividad de la aplicación..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8800/api/ | grep -q "200\|401\|403"; then
    echo "✅ Aplicación responde correctamente"
else
    echo "⚠️  Aplicación no responde (puede estar iniciando)"
fi

# Verificar base de datos
echo "🗄️ Verificando base de datos..."
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U mini_erp_user &> /dev/null; then
    echo "✅ Base de datos está funcionando"
else
    echo "❌ Base de datos no está funcionando"
fi

# Mostrar logs recientes
echo "📋 Logs recientes de la aplicación:"
docker-compose -f docker-compose.prod.yml logs --tail=10 web

echo ""
echo "🎉 Verificación completada!"
echo "🌐 Aplicación disponible en: http://localhost:8800"
