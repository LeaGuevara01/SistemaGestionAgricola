#!/bin/bash

# 🐳 Scripts de Docker para Sistema de Gestión Agrícola

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ===== COMANDOS PRINCIPALES =====

# Iniciar todo el stack
start() {
    log "🚀 Iniciando Sistema de Gestión Agrícola..."
    docker-compose up -d
    log "✅ Sistema iniciado en:"
    log "   🌐 Frontend: http://localhost:5173"
    log "   🐍 Backend:  http://localhost:5000"
    log "   📊 Admin BD: http://localhost:8080"
}

# Parar todo el stack
stop() {
    log "⏹️  Deteniendo servicios..."
    docker-compose down
    log "✅ Servicios detenidos"
}

# Limpiar todo (contenedores, volúmenes, imágenes)
clean() {
    warn "🧹 Limpiando todo el entorno Docker..."
    read -p "¿Estás seguro? Esto eliminará TODOS los datos (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -f
        log "✅ Limpieza completada"
    else
        log "❌ Limpieza cancelada"
    fi
}

# Reconstruir imágenes
rebuild() {
    log "🔨 Reconstruyendo imágenes..."
    docker-compose build --no-cache
    log "✅ Imágenes reconstruidas"
}

# Ver logs en tiempo real
logs() {
    service=${1:-""}
    if [ -z "$service" ]; then
        log "📋 Mostrando logs de todos los servicios..."
        docker-compose logs -f
    else
        log "📋 Mostrando logs de $service..."
        docker-compose logs -f "$service"
    fi
}

# Estado de servicios
status() {
    log "📊 Estado de servicios:"
    docker-compose ps
    echo
    log "🔍 Health checks:"
    docker-compose exec backend curl -f http://localhost:5000/health 2>/dev/null && echo "✅ Backend OK" || echo "❌ Backend FAIL"
    docker-compose exec frontend curl -f http://localhost:5173 2>/dev/null && echo "✅ Frontend OK" || echo "❌ Frontend FAIL"
}

# Entrar a contenedor
shell() {
    service=${1:-backend}
    log "🐚 Entrando a shell de $service..."
    if [ "$service" = "backend" ]; then
        docker-compose exec backend bash
    elif [ "$service" = "frontend" ]; then
        docker-compose exec frontend sh
    elif [ "$service" = "postgres" ]; then
        docker-compose exec postgres psql -U elorza -d sistema_gestion_agricola
    else
        docker-compose exec "$service" sh
    fi
}

# Backup de base de datos
backup() {
    log "💾 Creando backup de base de datos..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose exec postgres pg_dump -U elorza sistema_gestion_agricola > "backup_${timestamp}.sql"
    log "✅ Backup creado: backup_${timestamp}.sql"
}

# Desarrollo - hot reload
dev() {
    log "🔧 Iniciando en modo desarrollo..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
}

# ===== MENU INTERACTIVO =====
menu() {
    echo -e "${BLUE}"
    echo "🐳 Docker Manager - Sistema Gestión Agrícola"
    echo "=============================================="
    echo -e "${NC}"
    echo "1) 🚀 Iniciar servicios"
    echo "2) ⏹️  Parar servicios" 
    echo "3) 📊 Ver estado"
    echo "4) 📋 Ver logs"
    echo "5) 🔨 Reconstruir"
    echo "6) 🐚 Shell (backend/frontend/postgres)"
    echo "7) 💾 Backup BD"
    echo "8) 🧹 Limpiar todo"
    echo "9) 🔧 Modo desarrollo"
    echo "0) ❌ Salir"
    echo
}

# ===== MAIN =====
case "${1:-menu}" in
    start|up)       start ;;
    stop|down)      stop ;;
    clean)          clean ;;
    rebuild)        rebuild ;;
    logs)           logs "$2" ;;
    status|ps)      status ;;
    shell|sh)       shell "$2" ;;
    backup)         backup ;;
    dev)            dev ;;
    menu)
        while true; do
            menu
            read -p "Selecciona una opción: " choice
            case $choice in
                1) start ;;
                2) stop ;;
                3) status ;;
                4) echo -n "Servicio (enter para todos): "; read service; logs "$service" ;;
                5) rebuild ;;
                6) echo -n "Servicio (backend/frontend/postgres): "; read service; shell "$service" ;;
                7) backup ;;
                8) clean ;;
                9) dev ;;
                0) log "👋 ¡Hasta luego!"; exit 0 ;;
                *) error "Opción inválida" ;;
            esac
            echo
            read -p "Presiona Enter para continuar..."
        done
        ;;
    *)
        echo "Uso: $0 [start|stop|clean|rebuild|logs|status|shell|backup|dev|menu]"
        echo "Sin argumentos ejecuta el menú interactivo"
        ;;
esac
