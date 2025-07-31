#!/usr/bin/env powershell

<#
.SYNOPSIS
    Script para configurar PostgreSQL local para desarrollo
.DESCRIPTION
    Instala PostgreSQL, crea la base de datos de desarrollo y configura el entorno
#>

param(
    [string]$Password = "password",
    [string]$DatabaseName = "elorza_dev",
    [string]$Username = "postgres"
)

Write-Host "🐘 === CONFIGURACIÓN POSTGRESQL LOCAL ===" -ForegroundColor Blue
Write-Host ""

# Función para verificar si un comando existe
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Verificar si PostgreSQL ya está instalado
if (Test-CommandExists "psql") {
    Write-Host "✅ PostgreSQL ya está instalado" -ForegroundColor Green
    
    # Verificar versión
    $pgVersion = psql --version
    Write-Host "   Versión: $pgVersion" -ForegroundColor Cyan
} else {
    Write-Host "❌ PostgreSQL no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para instalar PostgreSQL:" -ForegroundColor Yellow
    Write-Host "1. Usando Chocolatey:" -ForegroundColor White
    Write-Host "   choco install postgresql" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Usando Scoop:" -ForegroundColor White
    Write-Host "   scoop install postgresql" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Descarga manual desde:" -ForegroundColor White
    Write-Host "   https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host ""
    
    $install = Read-Host "¿Intentar instalación automática con Chocolatey? (y/N)"
    if ($install -eq "y" -or $install -eq "Y") {
        if (Test-CommandExists "choco") {
            Write-Host "📦 Instalando PostgreSQL con Chocolatey..." -ForegroundColor Blue
            choco install postgresql -y
            
            # Esperar a que la instalación termine
            Start-Sleep -Seconds 10
            
            # Verificar instalación
            if (Test-CommandExists "psql") {
                Write-Host "✅ PostgreSQL instalado correctamente" -ForegroundColor Green
            } else {
                Write-Host "❌ Error en la instalación. Instala manualmente." -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "❌ Chocolatey no encontrado. Instala PostgreSQL manualmente." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Instala PostgreSQL y ejecuta este script nuevamente." -ForegroundColor Red
        exit 1
    }
}

# Verificar si el servicio está ejecutándose
$pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    if ($pgService.Status -eq "Running") {
        Write-Host "✅ Servicio PostgreSQL ejecutándose" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Iniciando servicio PostgreSQL..." -ForegroundColor Yellow
        Start-Service $pgService.Name
        Write-Host "✅ Servicio PostgreSQL iniciado" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ Servicio PostgreSQL no encontrado, puede que ya esté ejecutándose" -ForegroundColor Yellow
}

# Crear base de datos de desarrollo
Write-Host ""
Write-Host "🏗️ Configurando base de datos de desarrollo..." -ForegroundColor Blue

$env:PGPASSWORD = $Password

# Verificar conexión
try {
    $null = psql -U $Username -d postgres -c "SELECT version();" 2>$null
    Write-Host "✅ Conexión a PostgreSQL exitosa" -ForegroundColor Green
} catch {
    Write-Host "❌ Error conectando a PostgreSQL" -ForegroundColor Red
    Write-Host "   Verifica usuario/contraseña: $Username/$Password" -ForegroundColor Yellow
    
    $newPassword = Read-Host "Ingresa la contraseña correcta para el usuario $Username" -AsSecureString
    $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($newPassword))
    $env:PGPASSWORD = $Password
}

# Verificar si la base de datos existe
$dbExists = psql -U $Username -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$DatabaseName';" 2>$null
if ($dbExists -match "1") {
    Write-Host "✅ Base de datos '$DatabaseName' ya existe" -ForegroundColor Green
} else {
    Write-Host "📦 Creando base de datos '$DatabaseName'..." -ForegroundColor Blue
    psql -U $Username -d postgres -c "CREATE DATABASE `"$DatabaseName`";" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos '$DatabaseName' creada" -ForegroundColor Green
    } else {
        Write-Host "❌ Error creando base de datos" -ForegroundColor Red
        exit 1
    }
}

# Crear archivo .env local
Write-Host ""
Write-Host "📝 Configurando variables de entorno..." -ForegroundColor Blue

$envFile = ".env.local"
$localUrl = "postgresql://${Username}:${Password}@localhost:5432/${DatabaseName}"

$envContent = @"
# Configuración PostgreSQL Local
LOCAL_POSTGRES_URL=$localUrl
DATABASE_URL=
SECRET_KEY=dev-secret-key-$(Get-Date -Format 'yyyyMMdd')
FLASK_ENV=development
FLASK_APP=backend/run.py
PYTHONPATH=.

# Para usar PostgreSQL local en lugar de remoto, comenta DATABASE_URL
# Para usar remoto, descomenta y configura DATABASE_URL
"@

$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Host "✅ Archivo $envFile creado" -ForegroundColor Green

# Instalar psycopg2 en el entorno Python
Write-Host ""
Write-Host "🐍 Instalando dependencias Python..." -ForegroundColor Blue

Set-Location "backend"

# Verificar si existe entorno virtual
if (Test-Path "venv") {
    Write-Host "✅ Entorno virtual encontrado" -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Blue
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
}

# Instalar psycopg2
Write-Host "📦 Instalando psycopg2-binary..." -ForegroundColor Blue
pip install psycopg2-binary

Write-Host "📦 Instalando dependencias del proyecto..." -ForegroundColor Blue
pip install -r requirements.txt

Set-Location ".."

# Mostrar resumen
Write-Host ""
Write-Host "🎉 === CONFIGURACIÓN COMPLETADA ===" -ForegroundColor Green
Write-Host ""
Write-Host "✅ PostgreSQL instalado y configurado" -ForegroundColor Green
Write-Host "✅ Base de datos '$DatabaseName' creada" -ForegroundColor Green
Write-Host "✅ Variables de entorno configuradas" -ForegroundColor Green
Write-Host "✅ Dependencias Python instaladas" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Configuración:" -ForegroundColor Cyan
Write-Host "   Usuario: $Username" -ForegroundColor White
Write-Host "   Base de datos: $DatabaseName" -ForegroundColor White
Write-Host "   URL: $localUrl" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Próximos pasos:" -ForegroundColor Yellow
Write-Host "   1. Ejecuta el script de migración:" -ForegroundColor White
Write-Host "      python migrate_to_postgresql.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Inicia el servidor backend:" -ForegroundColor White
Write-Host "      cd backend && python run.py" -ForegroundColor Gray
Write-Host ""

# Preguntar si ejecutar migración automáticamente
$migrate = Read-Host "¿Ejecutar migración automáticamente ahora? (y/N)"
if ($migrate -eq "y" -or $migrate -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Ejecutando migración..." -ForegroundColor Blue
    python migrate_to_postgresql.py
}
