import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ProveedorForm from '@/components/forms/ProveedorForm';

const AgregarProveedor = () => {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/proveedores');
  };

  const handleCancel = () => {
    navigate('/proveedores');
  };

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
          Agregar Proveedor
        </h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <ProveedorForm
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default AgregarProveedor;