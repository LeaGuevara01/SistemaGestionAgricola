import { apiService } from './api';

export const estadisticasService = {
  // Obtener métricas generales
  getMetricas: async () => {
    try {
      const response = await apiService.get('/estadisticas/metricas');
      return response.data;
    } catch (error) {
      console.error('Error al obtener métricas:', error);
      return {
        totalComponentes: 0,
        totalMaquinas: 0,
        totalCompras: 0,
        valorTotalStock: 0
      };
    }
  },

  // Obtener datos para gráficos
  getGraficos: async () => {
    try {
      const response = await apiService.get('/estadisticas/graficos');
      return response.data;
    } catch (error) {
      console.error('Error al obtener gráficos:', error);
      return {
        comprasPorMes: [],
        componentesPorCategoria: [],
        stockPorProveedor: []
      };
    }
  },

  // Obtener resumen de compras
  getResumenCompras: async (fechaInicio, fechaFin) => {
    try {
      const params = new URLSearchParams();
      if (fechaInicio) params.append('fecha_inicio', fechaInicio);
      if (fechaFin) params.append('fecha_fin', fechaFin);
      
      const response = await apiService.get(`/estadisticas/compras?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener resumen de compras:', error);
      return {
        totalGastado: 0,
        cantidadCompras: 0,
        promedioPorCompra: 0
      };
    }
  },

  async getResumenStock() {
    const response = await apiService.get('/stock/resumen');
    return response.data;
  },

  async getEstadisticasGenerales() {
    const response = await apiService.get('/estadisticas/generales');
    return response.data;
  },

  async getMovimientosRecientes() {
    const response = await apiService.get('/estadisticas/movimientos-recientes');
    return response.data;
  },

  async getGraficosStock() {
    const response = await apiService.get('/estadisticas/graficos-stock');
    return response.data;
  },

  // Métodos adicionales para compatibilidad con las páginas
  async getResumenGeneral() {
    const response = await apiService.get('/estadisticas/resumen-general');
    return response.data;
  },

  async getComprasPorPeriodo(periodo = 'mes') {
    const response = await apiService.get(`/estadisticas/compras-periodo?periodo=${periodo}`);
    return response.data;
  },

  async getStockCritico() {
    const response = await apiService.get('/estadisticas/stock-critico');
    return response.data;
  },

  async getTopProveedores(periodo = 'mes') {
    const response = await apiService.get(`/estadisticas/top-proveedores?periodo=${periodo}`);
    return response.data;
  },

  async getAlertas() {
    const response = await apiService.get('/estadisticas/alertas');
    return response.data;
  }
};

export default estadisticasService;