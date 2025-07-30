import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Search, Truck, AlertCircle } from 'lucide-react';
import { useComponente, useComponenteMaquinas } from '@/hooks/useApi';

const MaquinaCard = ({ maquina }) => {
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
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {maquina.foto ? (
            <img
              src={`/static/fotos/${maquina.foto}`}
              alt={maquina.nombre}
              className="w-16 h-16 rounded-lg object-cover"
            />
          ) : (
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
              <Truck className="h-8 w-8 text-gray-400" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                <Link 
                  to={`/maquinas/editar/${maquina.id}`}
                  className="hover:text-green-600"
                >
                  {maquina.nombre}
                </Link>
              </h3>
              <p className="text-sm text-gray-500">
                {maquina.marca} {maquina.modelo}
              </p>
              {maquina.numero_serie && (
                <p className="text-xs text-gray-400">
                  S/N: {maquina.numero_serie}
                </p>
              )}
            </div>

            <Link
              to={`/maquinas/${maquina.id}/componentes`}
              className="text-sm text-green-600 hover:text-green-700 font-medium"
            >
              Ver componentes
            </Link>
          </div>

          <div className="mt-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Estado:</span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(maquina.estado)}`}>
                {maquina.estado?.charAt(0).toUpperCase() + maquina.estado?.slice(1)}
              </span>
            </div>

            {maquina.tipo && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Tipo:</span>
                <span className="text-sm font-medium">{maquina.tipo}</span>
              </div>
            )}

            {maquina.año && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Año:</span>
                <span className="text-sm font-medium">{maquina.año}</span>
              </div>
            )}

            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Horas de trabajo:</span>
              <span className="text-sm font-medium">{maquina.horas_trabajo || 0} hs</span>
            </div>

            {maquina.ubicacion && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Ubicación:</span>
                <span className="text-sm font-medium">{maquina.ubicacion}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const MaquinasComponente = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [filtros, setFiltros] = useState({
    search: ''
  });

  const { data: componente, loading: loadingComponente, error: errorComponente } = useComponente(id);
  const { 
    data: maquinasData, 
    loading: loadingMaquinas, 
    error: errorMaquinas 
  } = useComponenteMaquinas(id, filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  if (loadingComponente || loadingMaquinas) {
    return <div className="text-center py-8">Cargando...</div>;
  }

  if (errorComponente || errorMaquinas) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-red-800">Error al cargar los datos</h3>
        <p className="mt-1 text-sm text-red-600">
          {errorComponente || errorMaquinas}
        </p>
      </div>
    );
  }

  const maquinas = maquinasData?.data || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/componentes')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Máquinas que usan: {componente?.nombre}
          </h1>
          <p className="text-sm text-gray-500">
            {componente?.categoria || 'Sin categoría'} - {maquinas.length} máquina(s) usando este componente
          </p>
        </div>
      </div>

      {/* Información del componente */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start space-x-4">
          {componente?.foto ? (
            <img
              src={`/static/fotos/${componente.foto}`}
              alt={componente.nombre}
              className="w-20 h-20 rounded-lg object-cover"
            />
          ) : (
            <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center">
              <Truck className="h-10 w-10 text-gray-400" />
            </div>
          )}
          
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">{componente?.nombre}</h2>
            {componente?.descripcion && (
              <p className="text-gray-600 mt-1">{componente.descripcion}</p>
            )}
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
              {componente?.numero_parte && (
                <div>
                  <span className="text-gray-500">Número de parte:</span>
                  <p className="font-medium">{componente.numero_parte}</p>
                </div>
              )}
              
              {componente?.precio && (
                <div>
                  <span className="text-gray-500">Precio:</span>
                  <p className="font-medium">${componente.precio}</p>
                </div>
              )}
              
              {componente?.stock_actual !== undefined && (
                <div>
                  <span className="text-gray-500">Stock actual:</span>
                  <p className={`font-medium ${componente.stock_actual <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {componente.stock_actual}
                  </p>
                </div>
              )}

              <div>
                <Link
                  to={`/componentes/editar/${componente?.id}`}
                  className="text-green-600 hover:text-green-700 font-medium"
                >
                  Editar componente
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar máquinas..."
            value={filtros.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          />
        </div>
      </div>

      {/* Lista de máquinas */}
      {maquinas.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {maquinas.map((maquina) => (
            <MaquinaCard
              key={maquina.id}
              maquina={maquina}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Truck className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay máquinas usando este componente
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Este componente no está asignado a ninguna máquina actualmente.
          </p>
        </div>
      )}
    </div>
  );
};

export default MaquinasComponente;
