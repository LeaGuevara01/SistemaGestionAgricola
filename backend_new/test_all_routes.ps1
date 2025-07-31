# Script de prueba de todas las rutas del API
# Ejecutar desde PowerShell

Write-Host "🌾 REPORTE DE PRUEBAS - SISTEMA DE GESTIÓN AGRÍCOLA" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

$baseUrl = "http://127.0.0.1:5000"
$results = @()

# Función para probar endpoint
function Test-Endpoint {
    param([string]$url, [string]$description)
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        
        $result = [PSCustomObject]@{
            Endpoint = $url.Replace($baseUrl, "")
            Description = $description
            Status = $response.StatusCode
            Success = if ($data.success -eq $null) { "N/A" } else { $data.success }
            DataType = if ($data.data -eq $null) { "N/A" } else { $data.data.GetType().Name }
            Total = if ($data.total -eq $null) { "N/A" } else { $data.total }
            Message = if ($data.message -eq $null) { "N/A" } else { $data.message }
            Result = "✅ OK"
        }
        
        Write-Host "✅ $description : Status $($response.StatusCode)" -ForegroundColor Green
        if ($data.total -ne $null) {
            Write-Host "   └── Total items: $($data.total)" -ForegroundColor Gray
        }
        if ($data.message -ne $null) {
            Write-Host "   └── Message: $($data.message)" -ForegroundColor Gray
        }
        
        return $result
    }
    catch {
        $result = [PSCustomObject]@{
            Endpoint = $url.Replace($baseUrl, "")
            Description = $description
            Status = "ERROR"
            Success = "False"
            DataType = "N/A"
            Total = "N/A"
            Message = $_.Exception.Message
            Result = "❌ ERROR"
        }
        
        Write-Host "❌ $description : ERROR" -ForegroundColor Red
        Write-Host "   └── $($_.Exception.Message)" -ForegroundColor Red
        
        return $result
    }
}

Write-Host "🔍 PROBANDO RUTAS BÁSICAS" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/health" "Health Check"
$results += Test-Endpoint "$baseUrl/api/test" "API Test"

Write-Host ""
Write-Host "🔧 PROBANDO API COMPONENTES" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/componentes" "Lista de Componentes"
$results += Test-Endpoint "$baseUrl/api/v1/componentes/1" "Componente ID 1"
$results += Test-Endpoint "$baseUrl/api/v1/componentes/categorias" "Categorías de Componentes"
$results += Test-Endpoint "$baseUrl/api/v1/componentes/stock-bajo" "Componentes con Stock Bajo"

Write-Host ""
Write-Host "🚜 PROBANDO API MÁQUINAS" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/maquinas" "Lista de Máquinas"
$results += Test-Endpoint "$baseUrl/api/v1/maquinas/1" "Máquina ID 1"
$results += Test-Endpoint "$baseUrl/api/v1/maquinas/tipos" "Tipos de Máquinas"

Write-Host ""
Write-Host "🏢 PROBANDO API PROVEEDORES" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/proveedores" "Lista de Proveedores"
$results += Test-Endpoint "$baseUrl/api/v1/proveedores/1" "Proveedor ID 1"
$results += Test-Endpoint "$baseUrl/api/v1/proveedores/tipos" "Tipos de Proveedores"

Write-Host ""
Write-Host "🛒 PROBANDO API COMPRAS" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/compras" "Lista de Compras"
$results += Test-Endpoint "$baseUrl/api/v1/compras/1" "Compra ID 1"
$results += Test-Endpoint "$baseUrl/api/v1/compras/estados" "Estados de Compras"

Write-Host ""
Write-Host "📦 PROBANDO API STOCK" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/stock" "Lista de Stock"
$results += Test-Endpoint "$baseUrl/api/v1/stock/1" "Stock ID 1"

Write-Host ""
Write-Host "📊 PROBANDO API ESTADÍSTICAS" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$results += Test-Endpoint "$baseUrl/api/v1/estadisticas/dashboard" "Dashboard de Estadísticas"

Write-Host ""
Write-Host "📋 RESUMEN DE RESULTADOS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$successCount = ($results | Where-Object { $_.Status -eq 200 }).Count
$totalCount = $results.Count
$errorCount = $totalCount - $successCount

Write-Host "Total de endpoints probados: $totalCount" -ForegroundColor White
Write-Host "Exitosos: $successCount" -ForegroundColor Green
Write-Host "Con errores: $errorCount" -ForegroundColor Red
Write-Host ""

if ($errorCount -eq 0) {
    Write-Host "🎉 ¡TODAS LAS RUTAS FUNCIONAN CORRECTAMENTE!" -ForegroundColor Green
    Write-Host "El backend está listo para conectar con el frontend." -ForegroundColor Green
} else {
    Write-Host "⚠️  Hay $errorCount endpoints con problemas." -ForegroundColor Yellow
    Write-Host "Revisar los errores antes de conectar con el frontend." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 TABLA DETALLADA DE RESULTADOS" -ForegroundColor Cyan
Write-Host "-" * 60 -ForegroundColor Cyan

$results | Format-Table -AutoSize

Write-Host ""
Write-Host "🚀 READY FOR FRONTEND CONNECTION!" -ForegroundColor Green
