#!/bin/bash

set -e  # Salir si hay errores

echo "🔨 Building aplicación para producción..."

# Verificar que estamos en el directorio correcto
if [ ! -d "frontend" ]; then
    echo "❌ Error: No se encuentra el directorio 'frontend'"
    echo "   Asegúrate de ejecutar desde la raíz del proyecto"
    exit 1
fi

if [ ! -d "sistema_gestion_agricola" ]; then
    echo "❌ Error: No se encuentra el directorio 'sistema_gestion_agricola'"
    exit 1
fi

# Navegar a frontend y build
echo "📦 Building frontend con Vite..."
cd frontend

# Verificar package.json
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encuentra package.json en frontend"
    exit 1
fi

# Instalar dependencias y build
npm install
npm run build

# Verificar que el build fue exitoso
if [ ! -d "dist" ]; then
    echo "❌ Error: Build falló - no se generó directorio 'dist'"
    exit 1
fi

cd ..

# Copiar assets a Flask
echo "📋 Copiando assets a Flask..."
rm -rf sistema_gestion_agricola/static/dist
cp -r frontend/dist sistema_gestion_agricola/static/

# Verificar copia exitosa
if [ -d "sistema_gestion_agricola/static/dist" ]; then
    echo "✅ Build completado!"
    echo "📁 Assets copiados a: sistema_gestion_agricola/static/dist"
    echo "📄 Archivos generados:"
    ls -la sistema_gestion_agricola/static/dist/
else
    echo "❌ Error: Falló la copia de assets"
    exit 1
fi