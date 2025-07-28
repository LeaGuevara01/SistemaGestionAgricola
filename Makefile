.PHONY: dev build deploy clean logs stop

# Desarrollo local
dev:
    @echo "🚀 Iniciando entorno de desarrollo..."
    docker-compose up -d postgres
    @sleep 5
    docker-compose up -d backend frontend
    @echo "✅ Servicios iniciados en http://localhost:5000 y http://localhost:5173"

# Build para producción
build:
    @echo "🔨 Building aplicación..."
    cd frontend && npm install && npm run build
    rm -rf sistema_gestion_agricola/static/dist
    cp -r frontend/dist sistema_gestion_agricola/static/
    @echo "✅ Build completado!"

# Deploy a Render
deploy: build
    @echo "🚀 Deploying a Render..."
    git add .
    git commit -m "Deploy $$(date)" || true
    git push origin main
    @echo "✅ Deploy iniciado!"

# Ver logs
logs:
    docker-compose logs -f

# Parar servicios
stop:
    docker-compose down

# Limpiar containers e imágenes
clean:
    docker-compose down -v
    docker system prune -f