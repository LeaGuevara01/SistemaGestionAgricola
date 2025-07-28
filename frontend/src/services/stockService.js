import { apiService } from './api';

export const stockService = {
  async getMovimientos(filters = {}) {
    const response = await apiService.get('/stock', filters);
    return response.data;
  },

  async registrarMovimiento(movimiento) {
    const response = await apiService.post('/stock/movimiento', movimiento);
    return response.data;
  },

  async getBajoStock() {
    const response = await apiService.get('/stock/bajo-stock');
    return response.data;
  },

  async getResumen() {
    const response = await apiService.get('/stock/resumen');
    return response.data;
  }
};