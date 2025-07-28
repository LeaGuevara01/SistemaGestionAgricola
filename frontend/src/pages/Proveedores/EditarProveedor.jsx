import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useProveedor } from '@/hooks/useApi';
import ProveedorForm from '@/components/forms/ProveedorForm';

const EditarProveedor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: proveedor, loading, error } = useProveedor(id);

  const handleSuccess = () => {
    navigate('/proveedores');
  };

  const handleCancel = () => {
    navigate('/proveedores');
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (error) return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  if (!proveedor) return <div className="text-center py-4">Proveedor no encontrado</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/proveedores')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Editar Proveedor: {proveedor.nombre}
        </h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <ProveedorForm
          proveedor={proveedor}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default EditarProveedor;