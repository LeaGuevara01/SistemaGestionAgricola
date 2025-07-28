# 📋 Guía de Docker - Sistema de Gestión Agrícola

## 🏗️ Arquitectura de Contenedores

### Servicios Disponibles:

1. **🐘 PostgreSQL** (`postgres`)

   - Puerto: `5432`
   - Base de datos: `sistema_gestion_agricola`
   - Usuario: `elorza` / Password: `password123`
   - Volumen persistente para datos

2. **🐍 Backend Flask** (`backend`)

   - Puerto: `5000`
   - Framework: Flask + SQLAlchemy
   - Health check: `/health`
   - Auto-restart habilitado

3. **⚛️ Frontend React** (`frontend`)

   - Puerto: `5173` (desarrollo)
   - Framework: React + Vite
   - Hot reload activado
   - Proxy automático a backend

4. **🔧 Adminer** (`adminer`) - Opcional
   - Puerto: `8080`
   - Interface web para PostgreSQL
   - Perfil: `debug` (no se inicia por defecto)

## 🚀 Comandos de Docker

### Comandos Básicos:

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Parar servicios
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache

# Ver estado de servicios
docker-compose ps
```

### Scripts Personalizados:

```bash
# Usar script helper (Linux/Mac)
chmod +x scripts/docker.sh
./scripts/docker.sh menu

# Comandos específicos
./scripts/docker.sh start    # Iniciar
./scripts/docker.sh stop     # Parar
./scripts/docker.sh logs     # Ver logs
./scripts/docker.sh status   # Estado
./scripts/docker.sh clean    # Limpiar todo
```

### Windows PowerShell:

```powershell
# Usar comandos docker-compose directamente
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## 🐚 Acceso a Contenedores

### Backend Flask:

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Ejecutar comandos Flask
docker-compose exec backend python -c "from backend.app import create_app; print(create_app())"

# Ver logs específicos
docker-compose logs backend
```

### Base de Datos:

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U elorza -d sistema_gestion_agricola

# Backup manual
docker-compose exec postgres pg_dump -U elorza sistema_gestion_agricola > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U elorza -d sistema_gestion_agricola < backup.sql
```

### Frontend:

```bash
# Entrar al contenedor frontend
docker-compose exec frontend sh

# Instalar nuevas dependencias
docker-compose exec frontend npm install nueva-dependencia
```

## 📊 Monitoreo y Debug

### Health Checks:

```bash
# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:5173

# PostgreSQL health
docker-compose exec postgres pg_isready -U elorza
```

### URLs de Desarrollo:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000/api/v1
- **Health Check**: http://localhost:5000/health
- **Adminer**: http://localhost:8080 (con perfil debug)

### Logs Útiles:

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs específicos
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Últimas 50 líneas
docker-compose logs --tail=50 backend
```

## 🔧 Configuración Avanzada

### Variables de Entorno:

```bash
# Editar docker-compose.yml para cambiar:
FLASK_ENV=development          # o production
DATABASE_URL=postgresql://...  # URL de conexión
SECRET_KEY=tu-clave-secreta   # Clave Flask
```

### Profiles de Docker:

```bash
# Iniciar con Adminer (debug)
docker-compose --profile debug up -d

# Solo servicios principales
docker-compose up -d
```

### Volúmenes Persistentes:

- `postgres_data`: Datos de PostgreSQL
- `frontend_dist`: Build de React
- `./static`: Archivos estáticos (fotos, uploads)

## ⚠️ Troubleshooting

### Problemas Comunes:

1. **Puerto 5432 ocupado**:

   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "5433:5432"  # Usar puerto diferente
   ```

2. **Frontend no conecta a Backend**:

   - Verificar que backend esté ejecutándose
   - Revisar proxy en `vite.config.js`
   - Verificar CORS en Flask

3. **Base de datos no persiste**:

   - Verificar volumen `postgres_data`
   - No usar `docker-compose down -v` para parar

4. **Cambios no se reflejan**:
   - Frontend: Hot reload automático
   - Backend: Reiniciar contenedor o usar bind mount

### Limpieza Completa:

```bash
# CUIDADO: Elimina TODO
docker-compose down -v          # Para servicios y elimina volúmenes
docker system prune -f          # Limpia imágenes y cache
docker volume prune -f          # Elimina volúmenes huérfanos
```

## 🚀 Deploy en Producción

Para producción, usar:

- Variables de entorno seguras
- PostgreSQL externo (Render/AWS RDS)
- Reverse proxy (Nginx)
- SSL/TLS terminación
- Logging centralizado
