import { apiRequest } from '@/utils/api';

export const pagosService = {
  getAll: (filtros = {}) => {
    const params = new URLSearchParams();
    Object.keys(filtros).forEach(key => {
      if (filtros[key]) {
        params.append(key, filtros[key]);
      }
    });
    return apiRequest('GET', `/pagos?${params.toString()}`);
  },

  getById: (id) => 
    apiRequest('GET', `/pagos/${id}`),

  create: (data) => 
    apiRequest('POST', '/pagos', data),

  update: (id, data) => 
    apiRequest('PUT', `/pagos/${id}`, data),

  delete: (id) => 
    apiRequest('DELETE', `/pagos/${id}`),

  marcarComoPagado: (id, data = {}) => 
    apiRequest('PUT', `/pagos/${id}/marcar-pagado`, data),

  getResumen: () => 
    apiRequest('GET', '/pagos/resumen'),

  generarPagosAutomaticos: () => 
    apiRequest('POST', '/pagos/generar-automaticos'),

  getProximosVencer: (dias = 7) => 
    apiRequest('GET', `/pagos/proximos-vencer?dias=${dias}`)
};