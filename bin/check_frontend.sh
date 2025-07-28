#!/bin/bash

echo "🔍 Verificando configuración de frontend..."

cd frontend

if [ ! -f "package.json" ]; then
    echo "❌ No se encuentra package.json"
    exit 1
fi

echo "📦 Scripts disponibles:"
grep -A 10 '"scripts"' package.json

echo ""
echo "🔧 Dependencias principales:"
grep -A 5 '"dependencies"' package.json

if [ -f "vite.config.js" ]; then
    echo ""
    echo "⚡ Configuración de Vite encontrada"
else
    echo "❌ No se encuentra vite.config.js"
fi

cd ..
echo "✅ Verificación completada"