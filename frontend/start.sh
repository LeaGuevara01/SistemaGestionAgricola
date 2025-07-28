#!/bin/bash

echo "Iniciando desarrollo..."

# Función para limpiar procesos
cleanup() {
    echo "Deteniendo servicios..."
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar backend
echo "Iniciando backend en puerto 5000..."
cd backend && python run.py &

# Esperar un momento para que el backend inicie
sleep 3

# Iniciar frontend
echo "Iniciando frontend en puerto 5173..."
cd ../frontend && npm run dev &

echo "Servicios iniciados:"
echo "- Backend: http://localhost:5000"
echo "- Frontend: http://localhost:5173"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios"

wait