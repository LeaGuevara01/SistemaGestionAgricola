import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ComponenteForm from '@/components/forms/ComponenteForm';

const AgregarComponentes = () => {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/componentes');
  };

  const handleCancel = () => {
    navigate('/componentes');
  };

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
          Agregar Componente
        </h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <ComponenteForm
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default AgregarComponentes;