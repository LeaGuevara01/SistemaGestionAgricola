import { apiService } from './api';

export const componentesService = {
  async getAll(filters = {}) {
    const response = await apiService.get('/componentes', filters);
    return response.data;
  },

  async getById(id, includeRelations = false) {
    const response = await apiService.get(`/componentes/${id}`, { include_relations: includeRelations });
    return response.data;
  },

  async create(componente) {
    const response = await apiService.post('/componentes', componente);
    return response.data;
  },

  async update(id, componente) {
    const response = await apiService.put(`/componentes/${id}`, componente);
    return response.data;
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