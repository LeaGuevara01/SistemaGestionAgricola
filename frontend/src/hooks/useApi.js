import { useQuery } from '@tanstack/react-query';
import { componentesService } from '@/services/componentesService';
import { maquinasService } from '@/services/maquinasService';
import { maquinasComponentesService } from '@/services/maquinasComponentesService';
import { comprasService } from '@/services/comprasService';
import { proveedoresService } from '@/services/proveedoresService';
import { stockService } from '@/services/stockService';

// Hook genérico para API
export const useApi = (queryKey, queryFn, options = {}) => {
  const { data, isLoading: loading, error, refetch } = useQuery({
    queryKey,
    queryFn,
    ...options
  });

  return {
    data,
    loading,
    error: error?.message || error,
    refetch
  };
};

// Hooks específicos para Componentes
export const useComponentes = (filtros = {}) => {
  return useApi(
    ['componentes', filtros],
    () => componentesService.getAll(filtros)
  );
};

export const useComponente = (id) => {
  return useApi(
    ['componente', id],
    () => componentesService.getById(id, true),
    { enabled: !!id }
  );
};

// Hooks específicos para Máquinas
export const useMaquinas = (filtros = {}) => {
  return useApi(
    ['maquinas', filtros],
    () => maquinasService.getAll(filtros)
  );
};

export const useMaquina = (id) => {
  return useApi(
    ['maquina', id],
    () => maquinasService.getById(id, true),
    { enabled: !!id }
  );
};

// Hooks específicos para Máquinas-Componentes
export const useMaquinaComponentes = (maquinaId, filtros = {}) => {
  return useApi(
    ['maquina-componentes', maquinaId, filtros],
    () => maquinasComponentesService.getMaquinaComponentes(maquinaId, filtros),
    { enabled: !!maquinaId }
  );
};

export const useComponentesDisponibles = (maquinaId, filtros = {}) => {
  return useApi(
    ['componentes-disponibles', maquinaId, filtros],
    () => maquinasComponentesService.getComponentesDisponibles(maquinaId, filtros),
    { enabled: !!maquinaId }
  );
};

export const useComponenteMaquinas = (componenteId, filtros = {}) => {
  return useApi(
    ['componente-maquinas', componenteId, filtros],
    () => maquinasComponentesService.getComponenteMaquinas(componenteId, filtros),
    { enabled: !!componenteId }
  );
};

// Hooks específicos para Compras
export const useCompras = (filtros = {}) => {
  return useApi(
    ['compras', filtros],
    () => comprasService.getAll(filtros)
  );
};

export const useCompra = (id) => {
  return useApi(
    ['compra', id],
    () => comprasService.getById(id),
    { enabled: !!id }
  );
};

// Hooks específicos para Proveedores
export const useProveedores = (filtros = {}) => {
  return useApi(
    ['proveedores', filtros],
    () => proveedoresService.getAll(filtros)
  );
};

export const useProveedor = (id) => {
  return useApi(
    ['proveedor', id],
    () => proveedoresService.getById(id, true),
    { enabled: !!id }
  );
};