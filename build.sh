#!/bin/bash

echo "🔨 Instalando dependencias backend..."
pip install -r requirements.txt

echo "🔍 Verificando Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js disponible: $(node --version)"
    echo "✅ npm disponible: $(npm --version)"
    
    echo "🔨 Building frontend..."
    cd frontend
    
    echo "📁 Archivos en frontend:"
    ls -la
    
    echo "🔧 Instalando dependencias del frontend..."
    npm install
    
    echo "🏗️ Ejecutando build del frontend..."
    npm run build
    
    echo "📦 Verificando build..."
    ls -la dist/
    
    if [ -d "dist/assets" ]; then
        echo "✅ Assets encontrados:"
        ls -la dist/assets/
    else
        echo "❌ Assets no encontrados"
    fi
    
    cd ..
    echo "✅ Frontend build completado"
else
    echo "❌ Node.js no disponible. Usando archivos estáticos predefinidos."
    
    # Crear archivos estáticos mínimos como fallback
    mkdir -p frontend/dist/assets
    
    echo "// Fallback JS" > frontend/dist/assets/index.js
    echo "/* Fallback CSS */" > frontend/dist/assets/index.css
    
    cat > frontend/dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Gestión Agrícola - Elorza</title>
    <script type="module" crossorigin src="/assets/index.js"></script>
    <link rel="stylesheet" href="/assets/index.css">
</head>
<body>
    <div id="root">
        <div style="padding: 20px; text-align: center;">
            <h1>🚜 Sistema Gestión Agrícola - Elorza</h1>
            <p>Frontend en construcción...</p>
            <p><a href="/health">Verificar Backend</a></p>
            <p><a href="/api/v1/componentes/test">Probar API</a></p>
        </div>
    </div>
</body>
</html>
EOF
    
    echo "✅ Archivos de fallback creados"
fi

echo "📁 Estructura final:"
ls -la frontend/dist/ || echo "❌ frontend/dist no existe"
echo "✅ Build completado"
