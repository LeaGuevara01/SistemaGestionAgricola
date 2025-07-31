# 🌾 Backend Principal - Sistema de Gestión Agrícola

## 📄 Descripción

Backend Flask con datos simulados para desarrollo rápido del Sistema de Gestión Agrícola Elorza.

## ✅ Estado: COMPLETAMENTE FUNCIONAL

### 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python app.py
```

**Servidor:** http://127.0.0.1:5000

### 📋 Endpoints Disponibles (18 rutas)

#### 🔍 Sistema

- `GET /health` - Health check
- `GET /api/test` - Test de API

#### 🔧 Componentes

- `GET /api/v1/componentes` - Lista con filtros
- `GET /api/v1/componentes/{id}` - Componente específico
- `GET /api/v1/componentes/categorias` - Categorías
- `GET /api/v1/componentes/stock-bajo` - Stock bajo

#### 🚜 Máquinas

- `GET /api/v1/maquinas` - Lista con filtros
- `GET /api/v1/maquinas/{id}` - Máquina específica
- `GET /api/v1/maquinas/tipos` - Tipos disponibles

#### 🏢 Proveedores

- `GET /api/v1/proveedores` - Lista con filtros
- `GET /api/v1/proveedores/{id}` - Proveedor específico
- `GET /api/v1/proveedores/tipos` - Tipos disponibles

#### 🛒 Compras

- `GET /api/v1/compras` - Lista con filtros
- `GET /api/v1/compras/{id}` - Compra específica
- `GET /api/v1/compras/estados` - Estados disponibles

#### 📦 Stock

- `GET /api/v1/stock` - Inventario con filtros
- `GET /api/v1/stock/{id}` - Item específico

#### 📊 Estadísticas

- `GET /api/v1/estadisticas/dashboard` - Dashboard completo

### 🎯 Características

- ✅ **CORS configurado** para frontend React
- ✅ **Datos simulados realistas**
- ✅ **Filtros y búsquedas** implementados
- ✅ **Paginación** simulada
- ✅ **Manejo de errores** robusto
- ✅ **Respuestas JSON consistentes**
- ✅ **Documentación HTML integrada**
- ✅ **Sin dependencias de BD**

### 🔧 Dependencias

- Flask 2.3.3
- Flask-CORS 4.0.0

### 📊 Datos Mock Incluidos

- **3 Componentes** (Filtro aceite, Correa dentada, Batería)
- **2 Máquinas** (Tractores John Deere y New Holland)
- **3 Proveedores** (Repuestos, Transmisiones, ElectroAgro)
- **3 Compras** (Diferentes estados)
- **Stock** correspondiente

### 🎨 Frontend Compatible

Configurado para trabajar con:

- React en localhost:5173
- React en localhost:3000

### 🔮 Ventajas

1. **Desarrollo independiente** - Sin esperar BD
2. **Testing predecible** - Datos controlados
3. **Deploy simple** - Solo Flask
4. **Performance excelente** - En memoria
5. **Debugging fácil** - Sin complejidades

### 📝 Notas

- Ideal para **MVP y desarrollo frontend**
- Fácil migración a BD real cuando sea necesario
- Mantiene compatibilidad de API
- Base sólida para extensiones futuras
