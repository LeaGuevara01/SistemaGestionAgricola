#!/usr/bin/env powershell

Write-Host "🔄 Reiniciando servidor backend..." -ForegroundColor Blue

# Ir al directorio del backend
Set-Location "backend"

# Verificar si hay procesos Python ejecutándose en el puerto 5000
$processes = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "⚠️ Puerto 5000 en uso, terminando procesos..." -ForegroundColor Yellow
    $processIds = $processes | ForEach-Object { (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Id }
    $processIds | ForEach-Object { 
        if ($_) {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
            Write-Host "Proceso $_ terminado" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
}

# Verificar que Python está disponible
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Asegúrate de que Python esté instalado y en el PATH." -ForegroundColor Red
    exit 1
}

# Instalar dependencias si es necesario
if (!(Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Blue
    python -m venv venv
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

# Instalar/actualizar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Blue
pip install -r requirements.txt

# Configurar variables de entorno
$env:FLASK_ENV = "development"
$env:FLASK_APP = "run.py"

Write-Host "🚀 Iniciando servidor Flask..." -ForegroundColor Green
Write-Host "   Servidor disponible en: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Presiona Ctrl+C para detener" -ForegroundColor Cyan
Write-Host ""

# Iniciar el servidor
python run.py
