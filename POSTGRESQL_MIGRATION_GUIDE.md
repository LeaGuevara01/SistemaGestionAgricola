# 🐘 Guía de Migración a PostgreSQL

Esta guía te ayudará a migrar completamente tu aplicación de SQLite a PostgreSQL para eliminar los problemas de compatibilidad y mejorar el rendimiento.

## 🎯 Beneficios de la Migración

- ✅ **Consistencia**: Mismo motor en desarrollo y producción
- ✅ **Rendimiento**: Connection pooling y optimizaciones
- ✅ **Estabilidad**: Sin errores de transacciones abortadas
- ✅ **Escalabilidad**: Mejor manejo de concurrencia
- ✅ **Características avanzadas**: JSON, full-text search, etc.

## 🚀 Proceso de Migración

### Paso 1: Configurar PostgreSQL Local

```powershell
# Ejecutar script de configuración automática
.\setup_postgresql_dev.ps1
```

O manualmente:

1. **Instalar PostgreSQL**:

   - Con Chocolatey: `choco install postgresql`
   - Con Scoop: `scoop install postgresql`
   - Descarga manual: https://www.postgresql.org/download/windows/

2. **Crear base de datos**:
   ```sql
   CREATE DATABASE elorza_dev;
   ```

### Paso 2: Ejecutar Migración

```bash
# Migrar datos y configuración
python migrate_to_postgresql.py
```

El script automáticamente:

- ✅ Instala dependencias Python necesarias
- ✅ Crea el esquema en PostgreSQL
- ✅ Migra todos los datos desde SQLite
- ✅ Actualiza la configuración del backend
- ✅ Configura variables de entorno

### Paso 3: Verificar Migración

```bash
# Iniciar servidor con PostgreSQL
cd backend
python run.py
```

Deberías ver:

```
🐘 Usando PostgreSQL local para desarrollo
✅ Esquema PostgreSQL creado
📋 Tablas encontradas en BD: ['componentes', 'maquinas', 'proveedores', ...]
```

## 🔧 Configuración de Variables de Entorno

### Desarrollo Local

```env
# .env.local
LOCAL_POSTGRES_URL=postgresql://postgres:password@localhost:5432/elorza_dev
DATABASE_URL=  # Vacío para usar PostgreSQL local
FLASK_ENV=development
```

### Producción (Render)

```env
# Variables en Render
DATABASE_URL=postgresql://user:pass@host:port/database  # URL de Render
FLASK_ENV=production
```

## 🔄 Flujo de Trabajo Recomendado

### Para Desarrollo:

1. Usar PostgreSQL local (`LOCAL_POSTGRES_URL`)
2. Mantener datos de prueba localmente
3. Sincronizar cambios de esquema con migraciones

### Para Producción:

1. Usar PostgreSQL de Render (`DATABASE_URL`)
2. Aplicar migraciones automáticamente
3. Backup regular de datos

## 🚨 Resolución de Problemas Comunes

### Error "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### Error de conexión PostgreSQL

1. Verificar que PostgreSQL esté ejecutándose:
   ```powershell
   Get-Service postgresql*
   ```
2. Verificar credenciales en `LOCAL_POSTGRES_URL`
3. Verificar que el puerto 5432 esté disponible

### Error "database does not exist"

```sql
-- Conectar como superusuario y crear BD
CREATE DATABASE elorza_dev;
GRANT ALL PRIVILEGES ON DATABASE elorza_dev TO postgres;
```

### Transacciones lentas

- El script incluye optimizaciones automáticas de PostgreSQL
- Connection pooling configurado para mejor rendimiento
- Queries optimizadas para grandes volúmenes de datos

## 📊 Optimizaciones Incluidas

### Connection Pooling

- Pool size: 10 conexiones permanentes
- Max overflow: 20 conexiones adicionales
- Pool timeout: 30 segundos
- Auto-recycle cada hora

### Configuración PostgreSQL

- work_mem: 256MB
- effective_cache_size: 1GB
- random_page_cost: 1.1 (para SSD)

### Índices Automáticos

- Índices en foreign keys
- Índices en fechas para consultas rápidas
- Índices en campos de búsqueda frecuente

## 🎯 Comandos Útiles

### Verificar estado de la migración:

```python
python -c "
from backend.app import create_app
from backend.app.utils.db_optimized import get_connection_info
app = create_app()
with app.app_context():
    print('🔍 Estado del pool:', get_connection_info())
"
```

### Backup de datos:

```bash
# Backup completo
pg_dump -h localhost -U postgres elorza_dev > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -h localhost -U postgres elorza_dev < backup_20250730.sql
```

### Monitorear rendimiento:

```sql
-- Queries más lentas
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## ✅ Checklist Post-Migración

- [ ] PostgreSQL local instalado y funcionando
- [ ] Base de datos `elorza_dev` creada
- [ ] Migración ejecutada sin errores
- [ ] Servidor backend inicia con PostgreSQL
- [ ] Endpoint `/api/v1/stock/resumen` funciona
- [ ] Datos migrados correctamente
- [ ] Variables de entorno configuradas
- [ ] Backup inicial creado

## 🚀 Próximos Pasos

1. **Eliminar SQLite**: Una vez verificada la migración
2. **Configurar CI/CD**: Para migraciones automáticas
3. **Monitoreo**: Implementar logging de rendimiento
4. **Backup automático**: Programar backups regulares

---

> 💡 **Tip**: Mantén tanto PostgreSQL local como remoto sincronizados usando el mismo esquema y migraciones para evitar discrepancias entre desarrollo y producción.
