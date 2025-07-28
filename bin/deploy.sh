#!/bin/bash

set -e

MESSAGE=${1:-"Deploy $(date '+%Y-%m-%d %H:%M:%S')"}

echo "🚀 Iniciando deploy a Render..."
echo "💬 Mensaje: $MESSAGE"

# Verificar que estamos en un repo git
if [ ! -d ".git" ]; then
    echo "❌ Error: No es un repositorio git"
    exit 1
fi

# Verificar branch
BRANCH=$(git branch --show-current)
echo "📍 Branch actual: $BRANCH"

if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
    echo "⚠️ Advertencia: No estás en main/master (actual: $BRANCH)"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deploy cancelado"
        exit 1
    fi
fi

# Build primero
echo "🔨 Ejecutando build..."
./build.sh

# Verificar estado de git
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Cambios detectados, commiteando..."
    git add .
    git commit -m "$MESSAGE"
else
    echo "ℹ️ No hay cambios para commitear"
fi

# Push a main
echo "📤 Pushing a Render..."
git push origin "$BRANCH"

echo "✅ Deploy iniciado!"
echo "🌐 Revisa tu dashboard en Render para el progreso"
echo "🔗 URL: https://dashboard.render.com/"