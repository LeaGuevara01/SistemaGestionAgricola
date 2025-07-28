import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useCompra } from '@/hooks/useApi';
import CompraForm from '@/components/forms/CompraForm';

const EditarCompra = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: compra, loading, error } = useCompra(id);

  const handleSuccess = () => {
    navigate('/compras');
  };

  const handleCancel = () => {
    navigate('/compras');
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (error) return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  if (!compra) return <div className="text-center py-4">Compra no encontrada</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/compras')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Editar Compra #{compra.id}
        </h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <CompraForm
          compra={compra}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default EditarCompra;