#!/bin/bash

echo "🔍 Verificando configuración completa..."

errors=0

# Verificar estructura de archivos
echo "📁 Verificando estructura..."
required_dirs=("frontend" "sistema_gestion_agricola" "scripts")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Falta directorio: $dir"
        ((errors++))
    else
        echo "✅ Directorio encontrado: $dir"
    fi
done

# Verificar archivos importantes
echo ""
echo "📄 Verificando archivos..."
required_files=("docker-compose.yml" "package.json" "frontend/package.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Falta archivo: $file"
        ((errors++))
    else
        echo "✅ Archivo encontrado: $file"
    fi
done

# Verificar Docker
echo ""
echo "🐳 Verificando Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker instalado"
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker corriendo"
    else
        echo "⚠️ Docker instalado pero no corriendo"
    fi
else
    echo "❌ Docker no instalado"
    ((errors++))
fi

# Verificar Node.js
echo ""
echo "📦 Verificando Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js instalado: $(node --version)"
else
    echo "❌ Node.js no instalado"
    ((errors++))
fi

# Verificar NPM
if command -v npm &> /dev/null; then
    echo "✅ NPM instalado: $(npm --version)"
else
    echo "❌ NPM no instalado"
    ((errors++))
fi

echo ""
if [ $errors -eq 0 ]; then
    echo "🎉 ¡Todo está en orden!"
    echo "🚀 Puedes ejecutar: ./dev.sh"
else
    echo "❌ Se encontraron $errors errores"
    echo "🔧 Corrige los errores antes de continuar"
fi