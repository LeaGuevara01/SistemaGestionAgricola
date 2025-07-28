import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Configurar axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para respuestas
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error || error.message || 'Error desconocido';
    toast.error(message);
    return Promise.reject(error);
  }
);

class ApiService {
  async request(endpoint, options = {}) {
    try {
      const response = await api.request({
        url: endpoint,
        ...options
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async get(endpoint, params = {}) {
    return this.request(endpoint, { method: 'GET', params });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, { method: 'POST', data });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, { method: 'PUT', data });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // Método especial para eliminar con POST (para tu backend)
  async deleteWithPost(endpoint, data = {}) {
    return this.request(endpoint, { method: 'POST', data });
  }

  async uploadFile(endpoint, file, onProgress) {
    const formData = new FormData();
    formData.append('photo', file);

    return this.request(endpoint, {
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: onProgress
    });
  }
}

export const apiService = new ApiService();