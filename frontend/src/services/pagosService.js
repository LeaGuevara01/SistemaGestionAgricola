import { apiService } from './api';

export const pagosService = {
  getAll: (filtros = {}) => {
    const params = new URLSearchParams();
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) {
        params.append(key, filtros[key]);
      }
    });
    return apiService.get(`/pagos?${params.toString()}`);
  },

  getById: (id) => 
    apiService.get(`/pagos/${id}`),

  create: (data) => 
    apiService.post('/pagos', data),

  update: (id, data) => 
    apiService.put(`/pagos/${id}`, data),

  delete: (id) => 
    apiService.delete(`/pagos/${id}`),

  marcarComoPagado: (id, data = {}) => 
    apiService.put(`/pagos/${id}/marcar-pagado`, data),

  getResumen: () => 
    apiService.get('/pagos/resumen'),

  generarPagosAutomaticos: () => 
    apiService.post('/pagos/generar-automaticos'),

  getProximosVencer: (dias = 7) => 
    apiService.get(`/pagos/proximos-vencer?dias=${dias}`)
};