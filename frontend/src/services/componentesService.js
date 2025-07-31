import { apiService } from './api';

export const componentesService = {
  async getAll(filters = {}) {
    const response = await apiService.get('/componentes', filters);
    // Si el response tiene estructura de API estándar, extraer el array de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async getById(id, includeRelations = false) {
    const response = await apiService.get(`/componentes/${id}`, { include_relations: includeRelations });
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async create(componente) {
    const response = await apiService.post('/componentes', componente);
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async update(id, componente) {
    const response = await apiService.put(`/componentes/${id}`, componente);
    // Si el response tiene estructura de API estándar, extraer el objeto de data
    if (response.success && response.data) {
      return response.data;
    }
    // Fallback para compatibilidad
    return response.data || response;
  },

  async delete(id) {
    console.log('Eliminando componente:', id); // Debug
    const response = await apiService.deleteWithPost(`/componentes/${id}/eliminar`);
    return response.data;
  },

  async uploadPhoto(id, file, onProgress) {
    const response = await apiService.uploadFile(`/componentes/${id}/upload-photo`, file, onProgress);
    return response.data;
  },

  async getCategorias() {
    const response = await apiService.get('/componentes/categorias');
    return response.data;
  }
};
