# Script de prueba de todas las rutas del API
Write-Host "Sistema de Gestion Agricola - Prueba de Rutas" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""

$baseUrl = "http://127.0.0.1:5000"

# Funcion para probar endpoint
function Test-Endpoint {
    param([string]$url, [string]$description)
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "OK $description : Status $($response.StatusCode)" -ForegroundColor Green
        if ($data.total -ne $null) {
            Write-Host "   Total items: $($data.total)" -ForegroundColor Gray
        }
        if ($data.message -ne $null) {
            Write-Host "   Message: $($data.message)" -ForegroundColor Gray
        }
        
        return $true
    }
    catch {
        Write-Host "ERROR $description : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "PROBANDO RUTAS BASICAS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$success = 0
$total = 0

$total++; if (Test-Endpoint "$baseUrl/health" "Health Check") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/test" "API Test") { $success++ }

Write-Host ""
Write-Host "PROBANDO API COMPONENTES" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/componentes" "Lista de Componentes") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/componentes/1" "Componente ID 1") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/componentes/categorias" "Categorias de Componentes") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/componentes/stock-bajo" "Componentes con Stock Bajo") { $success++ }

Write-Host ""
Write-Host "PROBANDO API MAQUINAS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/maquinas" "Lista de Maquinas") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/maquinas/1" "Maquina ID 1") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/maquinas/tipos" "Tipos de Maquinas") { $success++ }

Write-Host ""
Write-Host "PROBANDO API PROVEEDORES" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/proveedores" "Lista de Proveedores") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/proveedores/1" "Proveedor ID 1") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/proveedores/tipos" "Tipos de Proveedores") { $success++ }

Write-Host ""
Write-Host "PROBANDO API COMPRAS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/compras" "Lista de Compras") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/compras/1" "Compra ID 1") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/compras/estados" "Estados de Compras") { $success++ }

Write-Host ""
Write-Host "PROBANDO API STOCK" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/stock" "Lista de Stock") { $success++ }
$total++; if (Test-Endpoint "$baseUrl/api/v1/stock/1" "Stock ID 1") { $success++ }

Write-Host ""
Write-Host "PROBANDO API ESTADISTICAS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$total++; if (Test-Endpoint "$baseUrl/api/v1/estadisticas/dashboard" "Dashboard de Estadisticas") { $success++ }

Write-Host ""
Write-Host "RESUMEN DE RESULTADOS" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

$errorCount = $total - $success

Write-Host "Total de endpoints probados: $total" -ForegroundColor White
Write-Host "Exitosos: $success" -ForegroundColor Green
Write-Host "Con errores: $errorCount" -ForegroundColor Red
Write-Host ""

if ($errorCount -eq 0) {
    Write-Host "TODAS LAS RUTAS FUNCIONAN CORRECTAMENTE!" -ForegroundColor Green
    Write-Host "El backend esta listo para conectar con el frontend." -ForegroundColor Green
} else {
    Write-Host "Hay $errorCount endpoints con problemas." -ForegroundColor Yellow
    Write-Host "Revisar los errores antes de conectar con el frontend." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "READY FOR FRONTEND CONNECTION!" -ForegroundColor Green
