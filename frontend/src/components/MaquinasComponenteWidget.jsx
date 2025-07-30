import React from 'react';
import { Link } from 'react-router-dom';
import { Truck, Plus, Package } from 'lucide-react';
import { useComponenteMaquinas } from '@/hooks/useApi';

const MaquinaResumen = ({ maquina }) => {
  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'operativo':
        return 'bg-green-100 text-green-800';
      case 'mantenimiento':
        return 'bg-yellow-100 text-yellow-800';
      case 'fuera_servicio':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
      {maquina.foto ? (
        <img
          src={`/static/fotos/${maquina.foto}`}
          alt={maquina.nombre}
          className="w-10 h-10 rounded object-cover"
        />
      ) : (
        <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
          <Truck className="h-5 w-5 text-gray-400" />
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {maquina.nombre}
        </p>
        <p className="text-xs text-gray-500 truncate">
          {maquina.marca} {maquina.modelo}
        </p>
      </div>
      
      <div className="text-xs">
        <span className={`px-2 py-1 rounded-full ${getEstadoColor(maquina.estado)}`}>
          {maquina.estado?.charAt(0).toUpperCase() + maquina.estado?.slice(1)}
        </span>
      </div>
    </div>
  );
};

const MaquinasComponenteWidget = ({ componenteId, className = '' }) => {
  const { 
    data: maquinasData, 
    loading, 
    error 
  } = useComponenteMaquinas(componenteId, {}, { enabled: !!componenteId });

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Truck className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Máquinas</h3>
        </div>
        <div className="text-center py-4">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-500 mr-2"></div>
            Cargando máquinas...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="flex items-center space-x-2 mb-4">
          <Truck className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Máquinas</h3>
        </div>
        <div className="text-center py-4 text-red-600 text-sm">
          Error al cargar máquinas
        </div>
      </div>
    );
  }

  const maquinas = maquinasData?.data || [];

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Truck className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">
            Máquinas ({maquinas.length})
          </h3>
        </div>
        
        <Link
          to={`/componentes/${componenteId}/maquinas`}
          className="text-sm text-green-600 hover:text-green-700 font-medium flex items-center space-x-1"
        >
          <span>Ver todas</span>
          <Plus className="h-4 w-4" />
        </Link>
      </div>

      {maquinas.length > 0 ? (
        <div className="space-y-3">
          {maquinas.slice(0, 5).map((maquina) => (
            <MaquinaResumen key={maquina.id} maquina={maquina} />
          ))}
          
          {maquinas.length > 5 && (
            <div className="text-center pt-2">
              <Link
                to={`/componentes/${componenteId}/maquinas`}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Ver {maquinas.length - 5} máquina(s) más
              </Link>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-6">
          <Truck className="mx-auto h-8 w-8 text-gray-400" />
          <h4 className="mt-2 text-sm font-medium text-gray-900">
            Sin máquinas asignadas
          </h4>
          <p className="mt-1 text-sm text-gray-500">
            Este componente no está asignado a ninguna máquina.
          </p>
          <div className="mt-3">
            <Link
              to="/maquinas"
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Truck className="h-4 w-4 mr-1" />
              Ir a máquinas
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaquinasComponenteWidget;
