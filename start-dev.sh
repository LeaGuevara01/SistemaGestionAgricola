#!/bin/bash

# Iniciar backend
echo "Iniciando backend..."
cd backend
python run.py &
BACKEND_PID=$!

# Iniciar frontend
echo "Iniciando frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Función para limpiar procesos al salir
cleanup() {
    echo "Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID
    exit
}

trap cleanup SIGINT SIGTERM

wait