# Build para producción
Write-Host "🔨 Building aplicación para producción..." -ForegroundColor Green

# Navegar a frontend y build
Set-Location frontend
Write-Host "📦 Building frontend con Vite..." -ForegroundColor Yellow
npm install
npm run build

# Copiar assets a Flask
Write-Host "📋 Copiando assets a Flask..." -ForegroundColor Yellow
if (Test-Path "../sistema_gestion_agricola/static/dist") {
    Remove-Item "../sistema_gestion_agricola/static/dist" -Recurse -Force
}
Copy-Item "dist" "../sistema_gestion_agricola/static/" -Recurse

Set-Location ..

Write-Host "✅ Build completado!" -ForegroundColor Green
Write-Host "📁 Assets copiados a: sistema_gestion_agricola/static/dist" -ForegroundColor Cyan