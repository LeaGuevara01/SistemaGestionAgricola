import React, { useState } from 'react';
import { X, Search, Package, Plus, Check } from 'lucide-react';
import { useComponentesDisponibles } from '@/hooks/useApi';
import { maquinasComponentesService } from '@/services/maquinasComponentesService';
import { toast } from 'react-hot-toast';
import { CATEGORIAS_COMPONENTES } from '@/utils/constants';

const ComponenteDisponibleCard = ({ componente, isSelected, onToggle }) => {
  return (
    <div 
      className={`bg-white border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'border-green-500 bg-green-50' : 'border-gray-200'
      }`}
      onClick={() => onToggle(componente.id)}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          {componente.foto ? (
            <img
              src={`/static/fotos/${componente.foto}`}
              alt={componente.nombre}
              className="w-12 h-12 rounded-lg object-cover"
            />
          ) : (
            <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
              <Package className="h-6 w-6 text-gray-400" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900 truncate">
                {componente.nombre}
              </h4>
              <p className="text-xs text-gray-500 truncate">
                {componente.categoria || 'Sin categoría'}
              </p>
              {componente.numero_parte && (
                <p className="text-xs text-gray-400">
                  P/N: {componente.numero_parte}
                </p>
              )}
            </div>
            
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
              isSelected 
                ? 'bg-green-500 border-green-500' 
                : 'border-gray-300'
            }`}>
              {isSelected && <Check className="h-3 w-3 text-white" />}
            </div>
          </div>

          {componente.descripcion && (
            <p className="text-xs text-gray-600 mt-1 line-clamp-2">
              {componente.descripcion}
            </p>
          )}

          <div className="flex justify-between items-center mt-2 text-xs">
            {componente.precio && (
              <span className="text-gray-500">${componente.precio}</span>
            )}
            {componente.stock_actual !== undefined && (
              <span className={`font-medium ${
                componente.stock_actual <= 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                Stock: {componente.stock_actual}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const AsignarComponentesModal = ({ maquina, onClose, onSuccess }) => {
  const [filtros, setFiltros] = useState({
    search: '',
    categoria: ''
  });
  const [componentesSeleccionados, setComponentesSeleccionados] = useState(new Set());
  const [isAssigning, setIsAssigning] = useState(false);

  const { 
    data: componentesData, 
    loading, 
    error,
    refetch 
  } = useComponentesDisponibles(maquina?.id, filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  const toggleComponente = (componenteId) => {
    const newSelected = new Set(componentesSeleccionados);
    if (newSelected.has(componenteId)) {
      newSelected.delete(componenteId);
    } else {
      newSelected.add(componenteId);
    }
    setComponentesSeleccionados(newSelected);
  };

  const handleAsignar = async () => {
    if (componentesSeleccionados.size === 0) {
      toast.error('Selecciona al menos un componente');
      return;
    }

    setIsAssigning(true);
    try {
      const componentesIds = Array.from(componentesSeleccionados);
      
      if (componentesIds.length === 1) {
        // Asignar individual
        await maquinasComponentesService.asignarComponente(maquina.id, componentesIds[0]);
        toast.success('Componente asignado correctamente');
      } else {
        // Asignar masivo
        const result = await maquinasComponentesService.asignarComponentesMasivo(maquina.id, componentesIds);
        toast.success(result.message);
        
        if (result.errores && result.errores.length > 0) {
          console.warn('Errores durante la asignación:', result.errores);
        }
      }

      onSuccess();
    } catch (error) {
      console.error('Error al asignar componentes:', error);
      toast.error(error.response?.data?.error || 'Error al asignar los componentes');
    } finally {
      setIsAssigning(false);
    }
  };

  const componentesDisponibles = componentesData?.data || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Asignar Componentes
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Selecciona los componentes para asignar a {maquina?.nombre}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Filtros */}
        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar componentes..."
                value={filtros.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <select
              value={filtros.categoria}
              onChange={(e) => handleFilterChange('categoria', e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Todas las categorías</option>
              {CATEGORIAS_COMPONENTES.map((cat) => (
                <option key={cat.categoria} value={cat.categoria}>
                  {cat.categoria}
                </option>
              ))}
            </select>
          </div>

          {componentesSeleccionados.size > 0 && (
            <div className="mt-4 p-3 bg-green-100 rounded-lg">
              <p className="text-sm text-green-800">
                {componentesSeleccionados.size} componente(s) seleccionado(s)
              </p>
            </div>
          )}
        </div>

        {/* Lista de componentes */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-500 mr-2"></div>
                Cargando componentes disponibles...
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-600">
              Error al cargar los componentes: {error}
            </div>
          ) : componentesDisponibles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {componentesDisponibles.map((componente) => (
                <ComponenteDisponibleCard
                  key={componente.id}
                  componente={componente}
                  isSelected={componentesSeleccionados.has(componente.id)}
                  onToggle={toggleComponente}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No hay componentes disponibles
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Todos los componentes ya están asignados a esta máquina o no hay componentes con los filtros aplicados.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleAsignar}
            disabled={componentesSeleccionados.size === 0 || isAssigning}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isAssigning ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Asignando...</span>
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                <span>Asignar ({componentesSeleccionados.size})</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AsignarComponentesModal;
