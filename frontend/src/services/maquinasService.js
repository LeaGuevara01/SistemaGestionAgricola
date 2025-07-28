// filepath: d:\Code\elorza\frontend\src\services\maquinasService.js
import { apiService } from './api';

export const maquinasService = {
  async getAll(filters = {}) {
    const response = await apiService.get('/maquinas', filters);
    return response.data;
  },

  async getById(id, includeRelations = false) {
    const response = await apiService.get(`/maquinas/${id}`, { include_relations: includeRelations });
    return response.data;
  },

  async create(maquina) {
    const response = await apiService.post('/maquinas', maquina);
    return response.data;
  },

  async update(id, maquina) {
    const response = await apiService.put(`/maquinas/${id}`, maquina);
    return response.data;
  },

  async delete(id) {
    const response = await apiService.delete(`/maquinas/${id}`);
    return response;
  },

  async uploadPhoto(id, file, onProgress) {
    const response = await apiService.uploadFile(`/maquinas/${id}/upload-photo`, file, onProgress);
    return response.data;
  }
};