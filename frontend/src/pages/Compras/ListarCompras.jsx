import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Edit, Trash2, ShoppingCart, Calendar, DollarSign } from 'lucide-react';
import { useCompras } from '@/hooks/useApi';
import { comprasService } from '@/services/comprasService';
import { toast } from 'react-hot-toast';
import { ESTADOS } from '@/config';

const CompraCard = ({ compra, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta compra?')) {
      try {
        await comprasService.delete(compra.id);
        toast.success('Compra eliminada correctamente');
        onDelete();
      } catch (error) {
        toast.error('Error al eliminar la compra');
      }
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case ESTADOS.COMPRA.PENDIENTE:
        return 'bg-yellow-100 text-yellow-800';
      case ESTADOS.COMPRA.ENTREGADO:
        return 'bg-green-100 text-green-800';
      case ESTADOS.COMPRA.CANCELADO:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-3">
            <ShoppingCart className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {compra.componente?.nombre || compra.maquina?.nombre}
            </h3>
            <p className="text-sm text-gray-500">
              {compra.proveedor?.nombre}
            </p>
            {compra.numero_factura && (
              <p className="text-xs text-gray-400">
                Factura: {compra.numero_factura}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/compras/editar/${compra.id}`}
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

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Estado:</span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(compra.estado)}`}>
            {compra.estado?.charAt(0).toUpperCase() + compra.estado?.slice(1)}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-sm text-gray-500">Fecha de compra:</span>
          <span className="text-sm font-medium flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            {new Date(compra.fecha_compra).toLocaleDateString()}
          </span>
        </div>

        {compra.fecha_entrega && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-500">Fecha de entrega:</span>
            <span className="text-sm font-medium">
              {new Date(compra.fecha_entrega).toLocaleDateString()}
            </span>
          </div>
        )}

        <div className="flex justify-between">
          <span className="text-sm text-gray-500">Cantidad:</span>
          <span className="text-sm font-medium">{compra.cantidad} unidades</span>
        </div>

        <div className="flex justify-between">
          <span className="text-sm text-gray-500">Precio unitario:</span>
          <span className="text-sm font-medium">${compra.precio_unitario}</span>
        </div>

        <div className="flex justify-between items-center pt-2 border-t">
          <span className="text-sm text-gray-500">Total:</span>
          <span className="text-lg font-bold text-green-600 flex items-center">
            <DollarSign className="h-4 w-4" />
            {compra.precio_total}
          </span>
        </div>
      </div>
    </div>
  );
};

const ListarCompras = () => {
  const [filtros, setFiltros] = useState({
    proveedor_id: '',
    estado: '',
    fecha_desde: '',
    fecha_hasta: '',
    include_relations: true
  });

  const { data: compras, loading, error, refetch } = useCompras(filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="text-center py-8">Cargando compras...</div>;
  if (error) return <div className="text-red-500 text-center py-8">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Compras</h1>
        <Link
          to="/compras/registrar"
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Registrar Compra</span>
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={filtros.estado}
              onChange={(e) => handleFilterChange('estado', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Todos los estados</option>
              <option value={ESTADOS.COMPRA.PENDIENTE}>Pendiente</option>
              <option value={ESTADOS.COMPRA.ENTREGADO}>Entregado</option>
              <option value={ESTADOS.COMPRA.CANCELADO}>Cancelado</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha desde
            </label>
            <input
              type="date"
              value={filtros.fecha_desde}
              onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha hasta
            </label>
            <input
              type="date"
              value={filtros.fecha_hasta}
              onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFiltros({
                proveedor_id: '',
                estado: '',
                fecha_desde: '',
                fecha_hasta: '',
                include_relations: true
              })}
              className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de compras */}
      {compras && compras.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {compras.map((compra) => (
            <CompraCard
              key={compra.id}
              compra={compra}
              onDelete={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay compras registradas
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza registrando una nueva compra.
          </p>
          <div className="mt-6">
            <Link
              to="/compras/registrar"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Registrar Compra
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListarCompras;