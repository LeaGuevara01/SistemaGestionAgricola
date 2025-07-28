// filepath: d:\Code\elorza\frontend\src\config\index.js
// Configuración general
export const APP_CONFIG = {
  NAME: import.meta.env.VITE_APP_NAME || 'Sistema Agrícola',
  VERSION: '1.0.0',
  COPYRIGHT: '2024 Sistema Agrícola'
};

// Estados de entidades
export const ESTADOS = {
  COMPRA: {
    PENDIENTE: 'pendiente',
    ENTREGADO: 'entregado',
    CANCELADO: 'cancelado'
  },
  MAQUINA: {
    OPERATIVO: 'operativo',
    MANTENIMIENTO: 'mantenimiento',
    FUERA_SERVICIO: 'fuera_servicio'
  }
};

// Tipos de movimiento de stock
export const TIPOS_MOVIMIENTO = {
  ENTRADA: 'entrada',
  SALIDA: 'salida',
  AJUSTE: 'ajuste'
};

// Categorías por defecto
export const CATEGORIAS_COMPONENTES = [
  'Filtros',
  'Aceites',
  'Repuestos Motor',
  'Sistema Hidráulico',
  'Transmisión',
  'Frenos',
  'Neumáticos',
  'Herramientas',
  'Otros'
];

// Rutas de navegación
export const ROUTES = {
  HOME: '/',
  COMPONENTES: '/componentes',
  MAQUINAS: '/maquinas',
  COMPRAS: '/compras',
  PROVEEDORES: '/proveedores',
  STOCK: '/stock',
  ESTADISTICAS: '/estadisticas',
  PAGOS: '/pagos'
};