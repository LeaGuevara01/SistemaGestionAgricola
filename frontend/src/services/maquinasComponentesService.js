import { apiService } from './api';

export const maquinasComponentesService = {
  // Obtener componentes asociados a una máquina
  async getMaquinaComponentes(maquinaId, filters = {}) {
    const response = await apiService.get(`/maquinas/${maquinaId}/componentes`, filters);
    return response.data;
  },

  // Obtener componentes disponibles para asignar a una máquina
  async getComponentesDisponibles(maquinaId, filters = {}) {
    const response = await apiService.get(`/maquinas/${maquinaId}/componentes/disponibles`, filters);
    return response.data;
  },

  // Asignar un componente a una máquina
  async asignarComponente(maquinaId, componenteId) {
    const response = await apiService.post(`/maquinas/${maquinaId}/componentes/${componenteId}`);
    return response.data;
  },

  // Desasignar un componente de una máquina
  async desasignarComponente(maquinaId, componenteId) {
    const response = await apiService.delete(`/maquinas/${maquinaId}/componentes/${componenteId}`);
    return response.data;
  },

  // Asignar múltiples componentes a una máquina
  async asignarComponentesMasivo(maquinaId, componentesIds) {
    const response = await apiService.post(`/maquinas/${maquinaId}/componentes/masivo`, {
      componentes_ids: componentesIds
    });
    return response.data;
  },

  // Obtener máquinas que usan un componente específico
  async getComponenteMaquinas(componenteId, filters = {}) {
    const response = await apiService.get(`/componentes/${componenteId}/maquinas`, filters);
    return response.data;
  }
};
