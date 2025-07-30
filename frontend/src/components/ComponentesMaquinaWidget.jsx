import React from 'react';
import { Link } from 'react-router-dom';
import { Package, Plus, Truck } from 'lucide-react';
import { useMaquinaComponentes } from '@/hooks/useApi';

const ComponenteResumen = ({ componente }) => {
  return (
    <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
      {componente.foto ? (
        <img
          src={`/static/fotos/${componente.foto}`}
          alt={componente.nombre}
          className="w-10 h-10 rounded object-cover"
        />
      ) : (
        <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
          <Package className="h-5 w-5 text-gray-400" />
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {componente.nombre}
        </p>
        <p className="text-xs text-gray-500 truncate">
          {componente.categoria || 'Sin categoría'}
        </p>
      </div>
      
      {componente.stock_actual !== undefined && (
        <div className="text-xs">
          <span className={`px-2 py-1 rounded-full ${
            componente.stock_actual <= 0 
              ? 'bg-red-100 text-red-800' 
              : 'bg-green-100 text-green-800'
          }`}>
            {componente.stock_actual}
          </span>
        </div>
      )}
    </div>
  );
};

const ComponentesMaquinaWidget = ({ maquinaId, className = '' }) => {
  const { 
    data: componentesData, 
    loading, 
    error 
  } = useMaquinaComponentes(maquinaId, {}, { enabled: !!maquinaId });

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Package className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Componentes</h3>
        </div>
        <div className="text-center py-4">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-500 mr-2"></div>
            Cargando componentes...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Package className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Componentes</h3>
        </div>
        <div className="text-center py-4 text-red-600 text-sm">
          Error al cargar componentes
        </div>
      </div>
    );
  }

  const componentes = componentesData?.data || [];

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Package className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">
            Componentes ({componentes.length})
          </h3>
        </div>
        
        <Link
          to={`/maquinas/${maquinaId}/componentes`}
          className="text-sm text-green-600 hover:text-green-700 font-medium flex items-center space-x-1"
        >
          <span>Gestionar</span>
          <Plus className="h-4 w-4" />
        </Link>
      </div>

      {componentes.length > 0 ? (
        <div className="space-y-3">
          {componentes.slice(0, 5).map((componente) => (
            <ComponenteResumen key={componente.id} componente={componente} />
          ))}
          
          {componentes.length > 5 && (
            <div className="text-center pt-2">
              <Link
                to={`/maquinas/${maquinaId}/componentes`}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Ver {componentes.length - 5} componente(s) más
              </Link>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-6">
          <Package className="mx-auto h-8 w-8 text-gray-400" />
          <h4 className="mt-2 text-sm font-medium text-gray-900">
            Sin componentes asignados
          </h4>
          <p className="mt-1 text-sm text-gray-500">
            Esta máquina no tiene componentes asignados.
          </p>
          <div className="mt-3">
            <Link
              to={`/maquinas/${maquinaId}/componentes`}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-4 w-4 mr-1" />
              Asignar componentes
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComponentesMaquinaWidget;
