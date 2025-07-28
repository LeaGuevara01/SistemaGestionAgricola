import { apiRequest } from '@/utils/api';

export const estadisticasService = {
  getResumenGeneral: () => 
    apiRequest('GET', '/estadisticas/resumen'),

  getComprasPorPeriodo: (periodo) => 
    apiRequest('GET', `/estadisticas/compras-periodo?periodo=${periodo}`),

  getStockCritico: () => 
    apiRequest('GET', '/estadisticas/stock-critico'),

  getTopProveedores: (periodo) => 
    apiRequest('GET', `/estadisticas/top-proveedores?periodo=${periodo}`),

  getGastosMensuales: () => 
    apiRequest('GET', '/estadisticas/gastos-mensuales'),

  getUsoComponentes: () => 
    apiRequest('GET', '/estadisticas/uso-componentes')
};