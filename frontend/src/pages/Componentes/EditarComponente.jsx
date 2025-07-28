import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useComponente } from '@/hooks/useApi';
import ComponenteForm from '@/components/forms/ComponenteForm';

const EditarComponente = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: componente, loading, error } = useComponente(id);

  const handleSuccess = () => {
    navigate('/componentes');
  };

  const handleCancel = () => {
    navigate('/componentes');
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (error) return <div className="text-red-500 text-center py-4">Error: {error}</div>;
  if (!componente) return <div className="text-center py-4">Componente no encontrado</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/componentes')}
          className="p-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Editar Componente: {componente.nombre}
        </h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <ComponenteForm
          componente={componente}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default EditarComponente;