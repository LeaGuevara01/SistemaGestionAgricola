import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Edit, Trash2, Users, Phone, Mail, MapPin } from 'lucide-react';
import { useProveedores } from '@/hooks/useApi';
import { proveedoresService } from '@/services/proveedoresService';
import { toast } from 'react-hot-toast';

const ProveedorCard = ({ proveedor, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este proveedor?')) {
      try {
        await proveedoresService.update(proveedor.id, { activo: false });
        toast.success('Proveedor eliminado correctamente');
        onDelete();
      } catch (error) {
        toast.error('Error al eliminar el proveedor');
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <Users className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {proveedor.nombre}
            </h3>
            {proveedor.razon_social && proveedor.razon_social !== proveedor.nombre && (
              <p className="text-sm text-gray-500">
                {proveedor.razon_social}
              </p>
            )}
            {proveedor.cuit && (
              <p className="text-xs text-gray-400">
                CUIT: {proveedor.cuit}
              </p>
            )}
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/proveedores/editar/${proveedor.id}`}
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
        {proveedor.telefono && (
          <div className="flex items-center text-sm text-gray-600">
            <Phone className="h-4 w-4 mr-2" />
            <span>{proveedor.telefono}</span>
          </div>
        )}

        {proveedor.email && (
          <div className="flex items-center text-sm text-gray-600">
            <Mail className="h-4 w-4 mr-2" />
            <span>{proveedor.email}</span>
          </div>
        )}

        {(proveedor.direccion || proveedor.ciudad) && (
          <div className="flex items-start text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              {proveedor.direccion && <div>{proveedor.direccion}</div>}
              {proveedor.ciudad && (
                <div>
                  {proveedor.ciudad}
                  {proveedor.provincia && `, ${proveedor.provincia}`}
                  {proveedor.codigo_postal && ` (${proveedor.codigo_postal})`}
                </div>
              )}
            </div>
          </div>
        )}

        {proveedor.contacto && (
          <div className="pt-2 border-t">
            <span className="text-xs text-gray-500">Contacto: </span>
            <span className="text-sm font-medium text-gray-700">{proveedor.contacto}</span>
          </div>
        )}

        <div className="pt-2 border-t">
          <div className="grid grid-cols-2 gap-4 text-xs">
            {proveedor.condicion_iva && (
              <div>
                <span className="text-gray-500">IVA: </span>
                <span className="font-medium">{proveedor.condicion_iva}</span>
              </div>
            )}
            {proveedor.forma_pago && (
              <div>
                <span className="text-gray-500">Pago: </span>
                <span className="font-medium">{proveedor.forma_pago}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ListarProveedores = () => {
  const [filtros, setFiltros] = useState({
    search: '',
    activo: true
  });

  const { data: proveedores, loading, error, refetch } = useProveedores(filtros);

  const handleFilterChange = (key, value) => {
    setFiltros(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="text-center py-8">Cargando proveedores...</div>;
  if (error) return <div className="text-red-500 text-center py-8">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Proveedores</h1>
        <Link
          to="/proveedores/agregar"
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Agregar Proveedor</span>
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar proveedores..."
              value={filtros.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

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

      {/* Lista de proveedores */}
      {proveedores && proveedores.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {proveedores.map((proveedor) => (
            <ProveedorCard
              key={proveedor.id}
              proveedor={proveedor}
              onDelete={refetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No hay proveedores registrados
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Comienza agregando un nuevo proveedor.
          </p>
          <div className="mt-6">
            <Link
              to="/proveedores/agregar"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Agregar Proveedor
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListarProveedores;