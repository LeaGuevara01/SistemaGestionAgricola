import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Edit, Trash2, Package, AlertTriangle } from 'lucide-react';
import { useComponentes } from '@/hooks/useApi';
import { componentesService } from '@/services/componentesService';
import { toast } from 'react-hot-toast';

const ComponenteCard = ({ componente, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este componente?')) {
      try {
        await componentesService.delete(componente.id);
        toast.success('Componente eliminado correctamente');
        onDelete();
      } catch (error) {
        toast.error('Error al eliminar el componente');
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          {componente.foto ? (
            <img
              src={`/static/fotos/${componente.foto}`}
              alt={componente.nombre}
              className="w-12 h-12 rounded-lg object-cover mr-3"
            />
          ) : (
            <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center mr-3">
              <Package className="h-6 w-6 text-gray-400" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {componente.nombre}
            </h3>
            {componente.numero_parte && (
              <p className="text-sm text-gray-500">
                P/N: {componente.numero_parte}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/componentes/editar/${componente.id}`}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
          >
            <Edit className="h-4 w-4" />
          </Link>
          <button
            onClick={handleDelete}
            className="p-2 text-red-600 hover:bg-red-50 rounded"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <p className="text-gray-600 mb-3 text-sm line-clamp-2">
        {componente.descripcion}
      </p>

      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-500">Categoría:</span>
        <span className="text-sm font-medium">{componente.categoria || 'Sin categoría'}</span>
      </div>

      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-500">Stock actual:</span>
        <span className={`text-sm font-medium ${
          componente.stock_actual <= componente.stock_minimo 
            ? 'text-red-600' 
            : 'text-green-600'
        }`}>
          {componente.stock_actual} unidades
          {componente.stock_actual <= componente.stock_minimo && (
            <AlertTriangle className="inline h-4 w-4 ml-1" />
          )}
        </span>
      </div>

      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">Precio:</span>
        <span className="text-lg font-bold text-green-600">
          ${componente.precio_unitario || 0}
        </span>
      </div>
    </div>
  );
};

const ListarComponentes = () => {
  const [filtros, setFiltros] = useState({
    search: '',
    categoria: '',
    activo: true
  });

  const { data: componentes, loading, error, refetch } = useComponentes(filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="text-center py-8">Cargando componentes...</div>;
  if (error) return <div className="text-red-500 text-center py-8">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Componentes</h1>
        <Link
          to="/componentes/agregar"
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Agregar Componente</span>
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <option value="Filtros">Filtros</option>
            <option value="Aceites">Aceites</option>
            <option value="Repuestos Motor">Repuestos Motor</option>
            <option value="Sistema Hidráulico">Sistema Hidráulico</option>
            <option value="Transmisión">Transmisión</option>
            <option value="Frenos">Frenos</option>
            <option value="Neumáticos">Neumáticos</option>
            <option value="Herramientas">Herramientas</option>
            <option value="Otros">Otros</option>
          </select>

          <select
            value={filtros.activo}
            onChange={(e) => handleFilterChange('activo', e.target.value === 'true')}
            className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </select>
        </div>
      </div>

      {/* Lista de componentes */}
      {componentes && componentes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {componentes.map((componente) => (
            <ComponenteCard
              key={componente.id}
              componente={componente}
              onDelete={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay componentes
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza agregando un nuevo componente.
          </p>
          <div className="mt-6">
            <Link
              to="/componentes/agregar"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Agregar Componente
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListarComponentes;