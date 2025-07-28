// filepath: d:\Code\elorza\frontend\src\utils\constants.js
export const TIPOS_MOVIMIENTO = {
  ENTRADA: 'entrada',
  SALIDA: 'salida',
  AJUSTE: 'ajuste'
};

export const CATEGORIAS_COMPONENTES = [
  'Filtros',
  'Aceites',
  'Repuestos Motor',
  'Sistema Hidráulico',
  'Transmisión',
  'Frenos',
  'Neumáticos',
  'Herramientas',
  'Motor',
  'Hidráulico',
  'Eléctrico',
  'Dirección',
  'Refrigeración',
  'Combustible',
  'Lubricación',
  'Suspensión',
  'Originales',
  'Repuestos',
  'Accesorios',
  'Mantenimiento',
  'Otros',
  'Otro',
];

export const ESTADOS_MAQUINA = {
  OPERATIVA: 'operativa',
  EN_MANTENIMIENTO: 'en_mantenimiento',
  FUERA_DE_SERVICIO: 'fuera_de_servicio'
};

export const TIPOS_COMPONENTE = {
  MOTOR: 'motor',
  TRANSMISION: 'transmision',
  HIDRAULICO: 'hidraulico',
  NEUMATICO: 'neumatico',
  FILTRO: 'filtro',
  OTRO: 'otro'
};

export default {
  CATEGORIAS_COMPONENTES,
  ESTADOS_MAQUINA,
  TIPOS_COMPONENTE
};
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