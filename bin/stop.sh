#!/bin/bash

echo "🛑 Deteniendo servicios..."

if [ -f "docker-compose.yml" ]; then
    docker-compose down
    echo "✅ Servicios detenidos"
else
    echo "❌ No se encuentra docker-compose.yml"
    exit 1
fi