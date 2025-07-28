# 📋 APIs Disponibles - Sistema de Gestión Agrícola

## 🔧 Administración

- `GET /api/v1/admin/db/info` - Información de la base de datos
- `POST /api/v1/admin/db/query` - Ejecutar consultas SQL directas

## 🔩 Componentes

- `GET /api/v1/componentes` - Listar componentes (con filtros: categoria, search)
- `GET /api/v1/componentes/test` - Test de conexión componentes
- `GET /api/v1/componentes/<id>` - Obtener componente específico
- `POST /api/v1/componentes` - Crear nuevo componente
- `PUT /api/v1/componentes/<id>` - Actualizar componente
- `POST /api/v1/componentes/<id>/eliminar` - Eliminar componente
- `GET /api/v1/componentes/categorias` - Obtener categorías disponibles
- `POST /api/v1/componentes/<id>/upload-photo` - Subir foto de componente

## 🚜 Máquinas

- `GET /api/v1/maquinas` - Listar máquinas (con filtros: search, tipo, estado)
- `POST /api/v1/maquinas` - Crear nueva máquina
- `GET /api/v1/maquinas/<id>` - Obtener máquina específica
- `PUT /api/v1/maquinas/<id>` - Actualizar máquina
- `POST /api/v1/maquinas/<id>/upload-photo` - Subir foto de máquina
- `POST /api/v1/maquinas/import` - Importar máquinas desde CSV
- `GET /api/v1/maquinas/import/template` - Descargar plantilla CSV
- `GET /api/v1/maquinas/stats` - Estadísticas de máquinas

## 🛒 Compras

- `GET /api/v1/compras` - Listar compras (con filtros: fecha_desde, fecha_hasta, proveedor_id)
- `POST /api/v1/compras` - Registrar nueva compra
- `GET /api/v1/compras/<id>` - Obtener compra específica
- `PUT /api/v1/compras/<id>` - Actualizar compra

## 🏢 Proveedores

- `GET /api/v1/proveedores` - Listar proveedores (con filtro: search)
- `POST /api/v1/proveedores` - Crear nuevo proveedor
- `GET /api/v1/proveedores/<id>` - Obtener proveedor específico
- `PUT /api/v1/proveedores/<id>` - Actualizar proveedor

## 📦 Stock

- `GET /api/v1/stock` - Consultar stock (con filtros: componente_id, search)
- `POST /api/v1/stock/movimiento` - Registrar movimiento de stock
- `GET /api/v1/stock/bajo-stock` - Obtener items con stock bajo
- `GET /api/v1/stock/resumen` - Resumen general de stock

## 🔍 Debug y Health Check

- `GET /health` - Health check del sistema
- `GET /test` - Test básico de API
- `GET /debug/componentes` - Debug específico de componentes
- `GET /debug/sql` - Comparación SQL directo vs SQLAlchemy

## 📝 Formato de Respuesta Estándar

```json
{
  "success": true|false,
  "data": [...],
  "message": "Mensaje descriptivo",
  "total": 0,
  "error": "Error message (si aplica)"
}
```

## 🔐 Configuración de CORS

- Habilitado para todas las rutas
- Soporta métodos: GET, POST, PUT, DELETE
- Headers permitidos: Content-Type, Authorization

## 📁 Upload de Archivos

- Máximo 16MB por archivo
- Formatos permitidos: .jpg, .jpeg, .png, .gif
- Rutas de almacenamiento:
  - Componentes: `/static/fotos/componentes/`
  - Máquinas: `/static/fotos/maquinas/`
