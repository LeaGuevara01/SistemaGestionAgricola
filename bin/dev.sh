#!/bin/bash

set -e

echo "🚀 Iniciando entorno de desarrollo..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Inicia Docker primero."
    exit 1
fi

# Verificar docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: No se encuentra docker-compose.yml"
    exit 1
fi

echo "📊 Iniciando base de datos..."
docker-compose up -d postgres

echo "⏳ Esperando que PostgreSQL esté listo..."
sleep 10

echo "🐍 Iniciando backend Flask..."
docker-compose up -d backend

echo "⚛️ Iniciando frontend Vite..."
docker-compose up -d frontend

echo ""
echo "✅ Servicios iniciados:"
echo "   📊 PostgreSQL: localhost:5432"
echo "   🐍 Backend:    http://localhost:5000"
echo "   ⚛️ Frontend:   http://localhost:5173"
echo ""
echo "📝 Para ver logs: docker-compose logs -f [servicio]"
echo "🛑 Para parar:   ./stop.sh"

# Mostrar estado de contenedores
echo ""
echo "📋 Estado de contenedores:"
docker-compose ps