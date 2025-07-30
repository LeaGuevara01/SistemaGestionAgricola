import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Edit, Trash2, Truck, AlertCircle, CheckCircle, Clock, Package } from 'lucide-react';
import { useMaquinas } from '@/hooks/useApi';
import { maquinasService } from '@/services/maquinasService';
import { toast } from 'react-hot-toast';
import { ESTADOS } from '@/config';

const MaquinaCard = ({ maquina, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta máquina?')) {
      try {
        await maquinasService.update(maquina.id, { activo: false });
        toast.success('Máquina eliminada correctamente');
        onDelete();
      } catch (error) {
        toast.error('Error al eliminar la máquina');
      }
    }
  };

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case ESTADOS.MAQUINA.OPERATIVO:
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case ESTADOS.MAQUINA.MANTENIMIENTO:
        return <Clock className="h-5 w-5 text-yellow-600" />;
      case ESTADOS.MAQUINA.FUERA_SERVICIO:
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case ESTADOS.MAQUINA.OPERATIVO:
        return 'bg-green-100 text-green-800';
      case ESTADOS.MAQUINA.MANTENIMIENTO:
        return 'bg-yellow-100 text-yellow-800';
      case ESTADOS.MAQUINA.FUERA_SERVICIO:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          {maquina.foto ? (
            <img
              src={`/static/fotos/${maquina.foto}`}
              alt={maquina.nombre}
              className="w-16 h-16 rounded-lg object-cover mr-4"
            />
          ) : (
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center mr-4">
              <Truck className="h-8 w-8 text-gray-400" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {maquina.nombre}
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
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/maquinas/${maquina.id}/componentes`}
            className="p-2 text-green-600 hover:bg-green-50 rounded"
            title="Ver componentes"
          >
            <Package className="h-4 w-4" />
          </Link>
          <Link
            to={`/maquinas/editar/${maquina.id}`}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
            title="Editar máquina"
          >
            <Edit className="h-4 w-4" />
          </Link>
          <button
            onClick={handleDelete}
            className="p-2 text-red-600 hover:bg-red-50 rounded"
            title="Eliminar máquina"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Estado:</span>
          <div className="flex items-center space-x-2">
            {getEstadoIcon(maquina.estado)}
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(maquina.estado)}`}>
              {maquina.estado?.charAt(0).toUpperCase() + maquina.estado?.slice(1)}
            </span>
          </div>
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
  );
};

const ListarMaquinas = () => {
  const [filtros, setFiltros] = useState({
    search: '',
    tipo: '',
    estado: '',
    activo: true
  });

  const { data: maquinas, loading, error, refetch } = useMaquinas(filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="text-center py-8">Cargando máquinas...</div>;
  if (error) return <div className="text-red-500 text-center py-8">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Máquinas</h1>
        <Link
          to="/maquinas/agregar"
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Agregar Máquina</span>
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar máquinas..."
              value={filtros.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
          
          <select
            value={filtros.tipo}
            onChange={(e) => handleFilterChange('tipo', e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="">Todos los tipos</option>
            <option value="Tractor">Tractor</option>
            <option value="Cosechadora">Cosechadora</option>
            <option value="Implemento">Implemento</option>
            <option value="Pulverizadora">Pulverizadora</option>
            <option value="Sembradora">Sembradora</option>
            <option value="Arado">Arado</option>
            <option value="Rastra">Rastra</option>
            <option value="Camión">Camión</option>
            <option value="Pickup">Pickup</option>
            <option value="Otro">Otro</option>
          </select>

          <select
            value={filtros.estado}
            onChange={(e) => handleFilterChange('estado', e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="">Todos los estados</option>
            <option value={ESTADOS.MAQUINA.OPERATIVO}>Operativo</option>
            <option value={ESTADOS.MAQUINA.MANTENIMIENTO}>Mantenimiento</option>
            <option value={ESTADOS.MAQUINA.FUERA_SERVICIO}>Fuera de Servicio</option>
          </select>

          <select
            value={filtros.activo}
            onChange={(e) => handleFilterChange('activo', e.target.value === 'true')}
            className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
          </select>
        </div>
      </div>

      {/* Lista de máquinas */}
      {maquinas && maquinas.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {maquinas.map((maquina) => (
            <MaquinaCard
              key={maquina.id}
              maquina={maquina}
              onDelete={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Truck className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay máquinas registradas
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza agregando una nueva máquina.
          </p>
          <div className="mt-6">
            <Link
              to="/maquinas/agregar"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Agregar Máquina
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListarMaquinas;