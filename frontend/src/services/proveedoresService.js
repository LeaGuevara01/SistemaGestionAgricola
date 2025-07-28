import { apiService } from './api';

const BASE = '/proveedores';

export const proveedoresService = {
  async getAll(filters = {}) {
    const response = await apiService.get(BASE, filters);
    return response.data;
  },

  async getById(id, includeRelations = false) {
    const response = await apiService.get(`${BASE}/${id}`, { include_relations: includeRelations });
    return response.data;
  },

  async create(proveedor) {
    const response = await apiService.post(BASE, proveedor);
    return response.data;
  },

  async update(id, proveedor) {
    const response = await apiService.put(`${BASE}/${id}`, proveedor);
    return response.data;
  },

  async delete(id) {
    const response = await apiService.delete(`${BASE}/${id}`);
    return response;
  }
};