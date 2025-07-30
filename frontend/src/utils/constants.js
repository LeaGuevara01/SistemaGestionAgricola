// filepath: d:\Code\elorza\frontend\src\utils\constants.js
export const TIPOS_MOVIMIENTO = {
  ENTRADA: 'entrada',
  SALIDA: 'salida',
  AJUSTE: 'ajuste'
};

export const CATEGORIAS_COMPONENTES = [
  {
    categoria: 'Motor',
    subcategorias: [
      'Repuestos Motor',
      'Correa',
      'Lubricación',
      'Refrigeración',
      'Combustible',
      'Filtros',
      'Aceites',
    ],
  },
  {
    categoria: 'Sistema Hidráulico',
    subcategorias: [
      'Hidráulico',
      'Bombas',
      'Válvulas',
      'Mangueras',
    ],
  },
  {
    categoria: 'Transmisión',
    subcategorias: [
      'Caja de cambios',
      'Embrague',
      'Cardan',
    ],
  },
  {
    categoria: 'Frenos',
    subcategorias: [
      'Pastillas',
      'Discos',
      'Cilindros',
    ],
  },
  {
    categoria: 'Dirección',
    subcategorias: [
      'Hidráulica',
      'Columnas',
      'Brazos',
    ],
  },
  {
    categoria: 'Suspensión',
    subcategorias: [
      'Amortiguadores',
      'Resortes',
      'Bujes',
    ],
  },
  {
    categoria: 'Neumáticos',
    subcategorias: [
      'Ruedas',
      'Llantas',
      'Cámaras',
    ],
  },
  {
    categoria: 'Eléctrico',
    subcategorias: [
      'Batería',
      'Luces',
      'Sensores',
      'Cables',
      'Alternador',
      'Arranque',
    ],
  },
  {
    categoria: 'Herramientas',
    subcategorias: [
      'Manuales',
      'Eléctricas',
      'Diagnóstico',
    ],
  },
  {
    categoria: 'Accesorios',
    subcategorias: [
      'Estéticos',
      'Funcionales',
      'Cabina',
    ],
  },
  {
    categoria: 'Mantenimiento',
    subcategorias: [
      'Revisión general',
      'Cambio de aceite',
      'Cambio de filtros',
    ],
  },
  {
    categoria: 'Originales',
    subcategorias: [
      'OEM',
      'Homologados',
    ],
  },
  {
    categoria: 'Repuestos',
    subcategorias: [
      'Genéricos',
      'Compatibles',
    ],
  },
  {
    categoria: 'Otros',
    subcategorias: [
      'Otro',
      'No clasificados',
    ],
  },
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