// filepath: d:\Code\elorza\frontend\src\hooks\useAuth.js
import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const login = async (credentials) => {
    try {
      const response = await apiService.post('/auth/login', credentials);
      setUser(response.user);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.post('/auth/logout');
      setUser(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al cerrar sesión');
    }
  };

  const checkAuth = async () => {
    try {
      const response = await apiService.get('/auth/me');
      setUser(response.user);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return { user, loading, error, login, logout };
};