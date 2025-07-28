#!/bin/bash

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📝 Mostrando logs de todos los servicios..."
    docker-compose logs -f
else
    echo "📝 Mostrando logs de: $SERVICE"
    docker-compose logs -f "$SERVICE"
fi