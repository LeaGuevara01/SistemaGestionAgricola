# Deploy a Render
param(
    [string]$message = "Deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Write-Host "🚀 Iniciando deploy a Render..." -ForegroundColor Green

# Build primero
& ".\bin\build.ps1"

# Verificar git status
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "📝 Cambios detectados, commiteando..." -ForegroundColor Yellow
    git add .
    git commit -m $message
} else {
    Write-Host "ℹ️ No hay cambios para commitear" -ForegroundColor Blue
}

# Push a main
Write-Host "📤 Pushing a Render..." -ForegroundColor Yellow
git push origin main

Write-Host "✅ Deploy iniciado!" -ForegroundColor Green
Write-Host "🌐 Revisa tu dashboard en Render para el progreso" -ForegroundColor Cyan