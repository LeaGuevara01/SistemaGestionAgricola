// filepath: d:\Code\elorza\frontend\src\services\maquinasService.js
import { apiService } from './api';

export const maquinasService = {
  async getAll(filters = {}) {
    const response = await apiService.get('/maquinas', filters);
    // Si el response tiene estructura de API estándar, extraer el array de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async getById(id, includeRelations = false) {
    const response = await apiService.get(`/maquinas/${id}`, { include_relations: includeRelations });
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async create(maquina) {
    const response = await apiService.post('/maquinas', maquina);
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async update(id, maquina) {
    const response = await apiService.put(`/maquinas/${id}`, maquina);
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
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