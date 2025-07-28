# Desarrollo completo con Docker
Write-Host "🚀 Iniciando entorno de desarrollo..." -ForegroundColor Green

# Verificar si Docker está corriendo
if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Desktop no está corriendo. Inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Construir y ejecutar servicios
docker-compose up --build -d postgres
Start-Sleep 5

Write-Host "📊 Iniciando base de datos..." -ForegroundColor Yellow
docker-compose up -d postgres

Write-Host "🐍 Iniciando backend Flask..." -ForegroundColor Yellow
docker-compose up -d backend

Write-Host "⚛️ Iniciando frontend Vite..." -ForegroundColor Yellow
docker-compose up -d frontend

Write-Host "" -ForegroundColor Green
Write-Host "✅ Servicios iniciados:" -ForegroundColor Green
Write-Host "   📊 PostgreSQL: localhost:5432" -ForegroundColor Cyan
Write-Host "   🐍 Backend:    http://localhost:5000" -ForegroundColor Cyan
Write-Host "   ⚛️ Frontend:   http://localhost:5173" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green
Write-Host "📝 Para ver logs: docker-compose logs -f [servicio]" -ForegroundColor Yellow
Write-Host "🛑 Para parar:   docker-compose down" -ForegroundColor Yellow