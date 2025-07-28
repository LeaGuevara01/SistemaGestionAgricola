#!/bin/bash

echo "🔧 Configurando permisos de scripts..."

# Hacer ejecutables todos los scripts
chmod +x *.sh

echo "✅ Scripts configurados:"
ls -la *.sh

echo ""
echo "📋 Scripts disponibles:"
echo "   ./dev.sh     - Iniciar desarrollo"
echo "   ./build.sh   - Build para producción"
echo "   ./deploy.sh  - Deploy a Render"
echo "   ./stop.sh    - Detener servicios"
echo "   ./logs.sh    - Ver logs"
echo ""
echo "🚀 Ejemplo de uso:"
echo "   ./setup.sh         # (este script, solo una vez)"
echo "   ./dev.sh           # Iniciar desarrollo"
echo "   ./logs.sh backend  # Ver logs del backend"
echo "   ./deploy.sh \"Nueva feature\""