import { apiService } from './api';

export const comprasService = {
  async getAll(filters = {}) {
    const response = await apiService.get('/compras', filters);
    return response.data;
  },

  async getById(id) {
    const response = await apiService.get(`/compras/${id}`);
    return response.data;
  },

  async create(compra) {
    const response = await apiService.post('/compras', compra);
    return response.data;
  },

  async update(id, compra) {
    const response = await apiService.put(`/compras/${id}`, compra);
    return response.data;
  },

  async delete(id) {
    const response = await apiService.delete(`/compras/${id}`);
    return response;
  }
};